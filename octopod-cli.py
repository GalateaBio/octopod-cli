#!/usr/bin/env python3
"""
Example usage:
    python octopod_cli.py \
        --username "user@example.com" \
        --password "your_password" \
        --file_to_process "data.vcf" \
        --model "skywalker" \
        --download_folder "results" \
        --check-if-file-exists

A script that:
  - Automatically picks upload mode: HTTP if file ≤ 50MB, SFTP if file > 50MB
  - Optionally reuses the newest existing file on the server if --check-if-file-exists
  - Uploads a file to GalateaBio (HTTP or SFTP), waits for validation, submits order, and downloads results.

Defaults:
  - 5h (300 min) timeouts for file validation & order completion
  - Poll interval of 60s (can be changed with --poll_interval)
  - Up to 5min wait after SFTP for the file to appear in the API
  - Uses token refresh; if refresh fails, re-auth with user/pass
"""

import argparse
import os
import time
import shutil
import requests
import paramiko
from typing import Optional, List, Dict, Any

# =======================================================================
# Adjust if you want a different threshold than 50 MB for HTTP vs. SFTP
MAX_HTTP_SIZE_MB = 50
# How long (in seconds) to wait after an SFTP upload for the file to appear in the API
SFTP_REFLECTION_TIMEOUT_SEC = 300
# How often (in seconds) to poll for the file's existence after SFTP
SFTP_REFLECTION_POLL_SEC = 30
# =======================================================================

API_ROOT = "https://api.dev.galatea.bio/api/v1"  # Dev environment
# API_ROOT = "https://api.galatea.bio/api/v1"    # Production environment

# Global store for credentials & tokens
CREDENTIALS = {
    "username": None,
    "password": None
}
TOKEN_STORE = {
    "access": None,
    "refresh": None
}


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments from sys.argv.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Uploads a file to GalateaBio automatically choosing HTTP or SFTP, waits for validation, submits order."
        )
    )
    parser.add_argument(
        "--username",
        required=True,
        help="Your GalateaBio Ancestry API username (email address)."
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Your GalateaBio Ancestry API password."
    )
    parser.add_argument(
        "--file_to_process",
        required=True,
        help=(
            "Path to the local file. If ≤ 50MB => direct HTTP upload. If >50MB => SFTP."
        )
    )
    parser.add_argument(
        "--check-if-file-exists",
        action="store_true",
        help=(
            "If set, the script checks if a file with the same name is already on the server. "
            "If found, re-uses the newest file by created_at. If not found, proceeds with upload."
        )
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Model name to use for execution (e.g. 'skywalker', 'mysterio_prs')."
    )
    parser.add_argument(
        "--download_folder",
        required=True,
        help="Folder path where the results will be saved."
    )
    parser.add_argument(
        "--poll_interval",
        type=int,
        default=60,
        help="Frequency in seconds to check status (default: 60)."
    )
    # SFTP args
    parser.add_argument(
        "--sftp_user",
        default="sftp-octopod-internal-cab6b8bf",
        help="Username for SFTP connection (default: sftp-octopod-internal-cab6b8bf)."
    )
    parser.add_argument(
        "--sftp_host",
        default="sftp.dev.galatea.bio",
        help="Hostname for SFTP (default: sftp.dev.galatea.bio)."
    )
    parser.add_argument(
        "--sftp_folder",
        default="octopod_cli_uploads",
        help="Remote folder for SFTP uploads if file not found (default: octopod_cli_uploads)."
    )
    parser.add_argument(
        "--sftp_password",
        default="",
        help="SFTP password if needed (otherwise assume key-based auth)."
    )
    parser.add_argument(
        "--sftp_keyfile",
        default="",
        help="Path to private key file for SFTP if needed."
    )
    return parser.parse_args()


def auth() -> None:
    """
    Authenticates with the GalateaBio Ancestry API using the username/password
    from CREDENTIALS. Updates TOKEN_STORE with new access/refresh tokens.
    """
    print("Attempting auth with username/password...")
    url = f"{API_ROOT}/users/auth"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {
        "email": CREDENTIALS["username"],
        "password": CREDENTIALS["password"]
    }
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
    tokens = resp.json()
    TOKEN_STORE["access"] = tokens["access"]
    TOKEN_STORE["refresh"] = tokens["refresh"]
    print("Authenticated successfully.")


def refresh_tokens() -> None:
    """
    Calls the refresh endpoint to update TOKEN_STORE with a new access token.
    If refresh fails (e.g., 400 or 401), raise an exception (caller does fallback).
    """
    if not TOKEN_STORE["refresh"]:
        raise RuntimeError("No refresh token available; cannot refresh.")

    print("Attempting token refresh...")
    url = f"{API_ROOT}/users/refresh"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN_STORE['access']}"
    }
    payload = {"refresh": TOKEN_STORE["refresh"]}
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()  # raises on 4xx/5xx

    tokens = resp.json()
    TOKEN_STORE["access"] = tokens["access"]
    TOKEN_STORE["refresh"] = tokens["refresh"]
    print("Token refreshed successfully!")


def safe_api_call(func, url: str, max_retries: int = 1, **kwargs) -> requests.Response:
    """
    Wraps a requests call to handle:
      1) On 401 Unauthorized => attempt refresh_tokens().
      2) If refresh fails => re-auth with user/pass.
      3) Retry original request once.

    Args:
        func: The requests function (e.g., requests.get, requests.post).
        url (str): The endpoint URL to call.
        max_retries (int): Number of times we can retry after a 401.

    Returns:
        requests.Response: The HTTP response object on success.

    Raises:
        HTTPError: If final request fails with 4xx/5xx.
    """
    try:
        resp = func(url, **kwargs)
        resp.raise_for_status()
        return resp
    except requests.exceptions.HTTPError as ex:
        if ex.response.status_code == 401 and max_retries > 0:
            print("Received 401 Unauthorized. Trying token refresh first...")
            try:
                refresh_tokens()
            except requests.exceptions.RequestException as refresh_ex:
                print(f"Refresh failed: {refresh_ex}. Falling back to full re-auth.")
                auth()
            # Update header with new access token
            if "headers" in kwargs:
                headers = kwargs["headers"]
                headers["Authorization"] = f"Bearer {TOKEN_STORE['access']}"
            return safe_api_call(func, url, max_retries=max_retries - 1, **kwargs)
        else:
            raise


def upload_file_http(local_file_path: str) -> str:
    """
    Uploads a local file to the GalateaBio Ancestry API and returns the new file ID.

    Args:
        local_file_path (str): Path to the file to upload.

    Returns:
        str: The file ID assigned by the server.
    """
    url = f"{API_ROOT}/data/files/upload"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN_STORE['access']}"
    }

    with open(local_file_path, "rb") as f:
        resp = safe_api_call(requests.post, url, headers=headers, files={"file": f})

    file_info = resp.json()
    return file_info["id"]


def sftp_upload(
    local_file_path: str,
    remote_filename: str,
    sftp_host: str,
    sftp_user: str,
    sftp_password: str,
    sftp_keyfile: str,
    sftp_folder: str
) -> None:
    """
    Uploads 'local_file_path' to SFTP with paramiko as 'remote_filename' inside 'sftp_folder'.

    Args:
        local_file_path (str): Path to the local file to upload.
        remote_filename (str): Destination filename on the SFTP server.
        sftp_host (str): Hostname of the SFTP server.
        sftp_user (str): Username for SFTP.
        sftp_password (str): Password for SFTP (if not using key-based auth).
        sftp_keyfile (str): Path to private key file for SFTP if needed.
        sftp_folder (str): Remote folder where the file will be placed.

    Raises:
        paramiko.ssh_exception.SSHException: If there's an SSH error.
    """
    print(f"SFTP uploading => {sftp_user}@{sftp_host}:{sftp_folder}/{remote_filename}")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    conn_kwargs = {
        "hostname": sftp_host,
        "username": sftp_user,
    }
    if sftp_password:
        conn_kwargs["password"] = sftp_password
    if sftp_keyfile:
        conn_kwargs["key_filename"] = sftp_keyfile

    ssh_client.connect(**conn_kwargs)

    try:
        with ssh_client.open_sftp() as sftp:
            # Create folder if needed
            try:
                sftp.chdir(sftp_folder)
            except IOError:
                sftp.mkdir(sftp_folder)
                sftp.chdir(sftp_folder)

            # Upload the file
            sftp.put(local_file_path, remote_filename)
    finally:
        ssh_client.close()

    print("SFTP upload complete.")


def find_newest_file_id_by_name(file_name: str) -> Optional[str]:
    """
    Searches the GalateaBio API for files matching 'file_name'.
    Sorts by created_at descending and returns the newest file's id.

    Args:
        file_name (str): The file name to search for on the server.

    Returns:
        Optional[str]: The file_id of the newest match, or None if none found.
    """
    url = f"{API_ROOT}/data/files?file={file_name}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN_STORE['access']}"
    }
    resp = safe_api_call(requests.get, url, headers=headers)
    data = resp.json()
    results = data.get("results", [])

    if not results:
        return None

    # Sort by created_at descending
    results.sort(key=lambda x: x["created_at"], reverse=True)

    newest = results[0]
    file_id = newest["id"]
    created_at = newest["created_at"]
    print(f"Found {len(results)} match(es) for name='{file_name}'.")
    print(f"Selecting newest file id={file_id}, created_at={created_at}.")
    return file_id


def wait_for_file_to_appear(
    file_name: str,
    timeout_sec: int = SFTP_REFLECTION_TIMEOUT_SEC,
    poll_sec: int = SFTP_REFLECTION_POLL_SEC
) -> Optional[str]:
    """
    After an SFTP upload, it can take a bit for the file to appear in the API.
    Poll every `poll_sec` for up to `timeout_sec`.

    Args:
        file_name (str): Name of the file to look for on the server.
        timeout_sec (int): Max time in seconds to wait.
        poll_sec (int): How often to poll in seconds.

    Returns:
        Optional[str]: The file_id if found, else None.
    """
    start = time.time()
    while (time.time() - start) < timeout_sec:
        file_id = find_newest_file_id_by_name(file_name)
        if file_id:
            return file_id
        print(f"File '{file_name}' not yet reflected in API. Waiting {poll_sec}s...")
        time.sleep(poll_sec)
    return None


def check_file_status(file_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves file info by file_id.

    Args:
        file_id (str): The UUID of the file on the server.

    Returns:
        Optional[Dict[str, Any]]:
            A dict with keys "check_completed", "acceptable", "amount_of_samples"
            or None if not found.
    """
    url = f"{API_ROOT}/data/files?file={file_id}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN_STORE['access']}"
    }
    resp = safe_api_call(requests.get, url, headers=headers)
    json_resp = resp.json()
    results = json_resp.get("results", [])
    if not results:
        return None

    file_entry = results[0]
    return {
        "check_completed": file_entry["check_completed"],
        "acceptable": file_entry["acceptable"],
        "amount_of_samples": file_entry["amount_of_samples"]
    }


def wait_for_file_validation(file_id: str, poll_interval: int = 60, timeout_minutes: int = 300) -> None:
    """
    Wait up to 5h for the file to become validated (check_completed + acceptable + has samples).
    Polls every `poll_interval`.

    Args:
        file_id (str): The UUID of the file on the server.
        poll_interval (int): Time between polls in seconds.
        timeout_minutes (int): Max time in minutes to wait.

    Raises:
        RuntimeError: If file is not found.
        TimeoutError: If validation doesn't complete in time.
    """
    start_time = time.time()
    max_time = timeout_minutes * 60

    while True:
        status = check_file_status(file_id)
        if status is None:
            raise RuntimeError(f"File with ID {file_id} not found on server.")

        if (status["check_completed"]
                and status["acceptable"]
                and status["amount_of_samples"] > 0):
            print("File is validated and ready for order submission.")
            return

        if (time.time() - start_time) > max_time:
            raise TimeoutError(f"File did not validate within {timeout_minutes} minutes.")

        print("File validation still in progress... waiting.")
        time.sleep(poll_interval)


def submit_order(file_id: str, model_name: str, tags_ids: Optional[List[str]] = None) -> str:
    """
    Submits an order. Returns order_id.

    Args:
        file_id (str): The file_id to process.
        model_name (str): The model name to use for execution.
        tags_ids (Optional[List[str]]): Additional tag IDs to apply.

    Returns:
        str: The newly created order's ID (UUID).
    """
    if tags_ids is None:
        tags_ids = []

    url = f"{API_ROOT}/exec/orders"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN_STORE['access']}"
    }
    payload = {
        "source_file_id": file_id,
        "model_name": model_name,
        "tags_ids": tags_ids
    }
    resp = safe_api_call(requests.post, url, headers=headers, json=payload)
    orders = resp.json()
    if isinstance(orders, list) and len(orders) > 0:
        return orders[0]["id"]
    else:
        return orders["id"]


def check_order_status(order_id: str) -> Optional[Dict[str, Any]]:
    """
    GET /exec/orders?filter={order_id}, returns an object with keys "status" and "result_types".
    result_types might be a list of strings or a list of dicts (e.g. [{"type": "SUMMARY_CHROMS", "label": "..."}, ...]).

    Args:
        order_id (str): The order UUID to check.

    Returns:
        Optional[Dict[str, Any]]:
            {
                "status": <str>,
                "result_types": <list>
            }
            or None if not found.
    """
    url = f"{API_ROOT}/exec/orders?filter={order_id}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN_STORE['access']}"
    }
    resp = safe_api_call(requests.get, url, headers=headers)
    json_resp = resp.json()
    results = json_resp.get("results", [])
    if not results:
        return None

    order_data = results[0]
    return {
        "status": order_data["status"],
        "result_types": order_data.get("result_types", [])
    }


def wait_for_order_completion(
    order_id: str,
    poll_interval: int = 60,
    timeout_minutes: int = 300
) -> List[Any]:
    """
    Wait up to 5h for order to complete. Poll every poll_interval.
    Raises on fail/cancel.

    Args:
        order_id (str): The order UUID.
        poll_interval (int): How often (in seconds) to poll.
        timeout_minutes (int): Max time (in minutes) to wait.

    Returns:
        list: The "result_types" once the order is completed (could be list of dicts or strings).
    """
    start_time = time.time()
    max_time = timeout_minutes * 60

    while True:
        info = check_order_status(order_id)
        if info is None:
            raise RuntimeError(f"Order with ID {order_id} not found.")
        status = info["status"]
        rtypes = info["result_types"]

        if status in ["Completed", "Reports failed"]:
            print(f"Order {order_id} finisihed with {status}.")
            return rtypes

        if status in ["Failed", "Canceled"]:
            raise RuntimeError(f"Order {order_id} is {status}. Stopping.")

        if (time.time() - start_time) > max_time:
            raise TimeoutError(
                f"Order {order_id} did not complete within {timeout_minutes} minutes."
            )

        print(f"Order status={status}. Waiting...")
        time.sleep(poll_interval)


def download_result(order_id: str, result_type: str, download_folder: str) -> None:
    """
    GET /data/results/{order_id}/download?result_type=... => saves file locally.

    Args:
        order_id (str): The order UUID.
        result_type (str): The string name for the result type (e.g. "SUMMARY_CHROMS").
        download_folder (str): Folder to save the downloaded file.

    Raises:
        requests.HTTPError: If the server responds with an error (e.g. 404).
    """
    url = f"{API_ROOT}/data/results/{order_id}/download?result_type={result_type}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {TOKEN_STORE['access']}"
    }
    resp = safe_api_call(requests.get, url, headers=headers, stream=True)

    resp.raise_for_status()  # if 404 or something, it raises an exception

    content_disp = resp.headers.get("content-disposition", "")
    if "filename=" in content_disp:
        filename_part = content_disp.split("filename=")[1].replace('"', "").strip()
        local_filename = filename_part
    else:
        local_filename = f"{order_id}_{result_type}.bin"

    local_path = os.path.join(download_folder, local_filename)
    with open(local_path, "wb") as f:
        shutil.copyfileobj(resp.raw, f)

    print(f"Downloaded {result_type} to {local_path}")


def find_or_upload_file(
    local_file_path: str,
    check_exists: bool,
    sftp_host: str,
    sftp_user: str,
    sftp_folder: str,
    sftp_password: str,
    sftp_keyfile: str
) -> str:
    """
    Determines the file ID by either reusing an existing (newest) file or uploading a new one (HTTP or SFTP).

    Args:
        local_file_path (str): Path to the local file to process.
        check_exists (bool): Whether to check for an existing file with the same name on the server.
        sftp_host, sftp_user, sftp_folder, sftp_password, sftp_keyfile: SFTP credentials.

    Returns:
        str: The file ID on the server.
    """
    file_basename = os.path.basename(local_file_path)
    file_id = None

    if check_exists:
        existing_id = find_newest_file_id_by_name(file_basename)
        if existing_id:
            print(f"Reusing newest file id={existing_id} with name={file_basename}.")
            file_id = existing_id

    if not file_id:
        file_size_mb = os.path.getsize(local_file_path) / (1024 * 1024)
        print(f"Local file size: {file_size_mb:.2f} MB")

        if file_size_mb <= MAX_HTTP_SIZE_MB:
            print(f"Using HTTP upload (≤ {MAX_HTTP_SIZE_MB} MB). Uploading {local_file_path}...")
            file_id = upload_file_http(local_file_path)
            print(f"HTTP upload complete. file_id={file_id}")
        else:
            print(f"Using SFTP upload (> {MAX_HTTP_SIZE_MB} MB).")
            print(f"No existing file found. SFTP uploading {local_file_path} to {file_basename}...")

            sftp_upload(
                local_file_path=local_file_path,
                remote_filename=file_basename,
                sftp_host=sftp_host,
                sftp_user=sftp_user,
                sftp_password=sftp_password,
                sftp_keyfile=sftp_keyfile,
                sftp_folder=sftp_folder
            )
            # Wait for reflection
            print("Waiting up to 5 minutes for the new file to appear in the GalateaBio API...")
            new_id = wait_for_file_to_appear(
                file_basename,
                timeout_sec=SFTP_REFLECTION_TIMEOUT_SEC,
                poll_sec=SFTP_REFLECTION_POLL_SEC
            )
            if not new_id:
                raise RuntimeError(
                    f"After SFTP upload, the file '{file_basename}' didn't appear "
                    f"in the API within {SFTP_REFLECTION_TIMEOUT_SEC}s."
                )
            file_id = new_id
            print(f"SFTP upload recognized. file_id={file_id}")

    return file_id


def process_order(
    file_id: str,
    model_name: str,
    download_folder: str,
    poll_interval: int
) -> None:
    """
    Submits an order for a validated file, waits for completion, and downloads all result types.

    Args:
        file_id (str): The file ID to process.
        model_name (str): Which model to use.
        download_folder (str): Where to save downloaded results.
        poll_interval (int): How often to check the order status (seconds).

    Raises:
        requests.HTTPError: If download fails with 4xx/5xx.
    """
    print("Waiting for file validation (up to 5h).")
    wait_for_file_validation(file_id, poll_interval=poll_interval, timeout_minutes=300)

    print(f"Submitting order with model='{model_name}' for file_id={file_id}...")
    order_id = submit_order(file_id, model_name)
    print(f"Order submitted successfully. order_id={order_id}")

    print("Waiting for order to complete (up to 5h).")
    result_types_raw = wait_for_order_completion(
        order_id,
        poll_interval=poll_interval,
        timeout_minutes=300
    )

    # Convert dict-based items to strings
    parsed_types: List[str] = []
    for item in result_types_raw:
        if isinstance(item, dict) and "type" in item:
            parsed_types.append(item["type"])  # e.g. "SUMMARY_CHROMS"
        elif isinstance(item, str):
            parsed_types.append(item)
        else:
            print(f"Skipping unknown result type item: {item}")

    print(f"Order completed. Available result types: {parsed_types}")

    print(f"Downloading results to folder: {download_folder}")
    os.makedirs(download_folder, exist_ok=True)

    for rt in parsed_types:
        try:
            download_result(order_id, rt, download_folder)
        except requests.HTTPError as e:
            print(f"Skipping result_type={rt} due to error: {e}")

    print("All done!")


def main() -> None:
    """
    Main entry point: parse args, authenticate, find or upload file, process order, download results.
    """
    args = parse_args()

    # Store credentials
    CREDENTIALS["username"] = args.username
    CREDENTIALS["password"] = args.password

    # 1. Auth
    auth()

    # 2. Find or upload the file, returning a file_id
    file_id = find_or_upload_file(
        local_file_path=args.file_to_process,
        check_exists=args.check_if_file_exists,
        sftp_host=args.sftp_host,
        sftp_user=args.sftp_user,
        sftp_folder=args.sftp_folder,
        sftp_password=args.sftp_password,
        sftp_keyfile=args.sftp_keyfile
    )

    # 3. Submit order, wait for completion, and download results
    process_order(
        file_id=file_id,
        model_name=args.model,
        download_folder=args.download_folder,
        poll_interval=args.poll_interval
    )


if __name__ == "__main__":
    main()
