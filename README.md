# Octopod wrapper

## Supported features:
* File uploading/downloading via API and SFTP
* Get organization's information and available models
* Searching files
* Submitting orders
* Cancelling orders
* Searching/adding/editing tags
* Downloading order's results

## Installation
```sh
git clone repository
```
In your project run 
```sh
pip install octopod file://<path_to_repo>
```

## Basic API & SFTP usage
```python
base_url = 'Octopod API URL'  # Example https://<OCTOPOD_API_HOST>
api_key = 'Octopod API Key'

octopod_client = OctopodClient(base_url=base_url, api_key=api_key)
# Web upload
file_obj = octopod_client.file_api.upload_file_from_file('/downloads/my_file.zip')
file_id = file_obj.get('id')
# SFTP upload
sftp_keyfile = 'File name with Octopod SFTP private key'
sftp_octopod_client = OctopodSftpClient(
  sftp_host='Octopod SFTP host',
  sftp_user='Octopod SFTP user',
  sftp_password=None,
  sftp_keyfile=sftp_keyfile,
)
file_name = sftp_octopod_client.upload_file_from_file(
  file_name='/downloads/my_file.zip',
  remote_filename='my_file.zip',
  remote_folder='my_awesome_folder_name',
)
files_obj = octopod_client.file_api.list_files(**{'file': file_name})
# Check that files_obj.get('count', 0) > 0
file_id = files_obj.get('results', [])[0].get('id')
# Waiting for file validating completion

org_info = octopod_client.organization_api.get_organization_info()
available_model_names = org_info.get('available_models', [])
# Found needed model name.
model_name = available_model_names[0]

order_obj = octopod_client.order_api.submit_order(file_id=file_id, model_name=model_name)
order_id = order_obj.get('id')
# Waiting for order execution completion

order_obj = octopod_client.order_api.find_order_by_id_or_file_id(order_id)
order_result_types = order_obj.get('result_types')
result_type = order_result_types[0]  
# or for example result_type = octopod_client.result_api.RESULT_TYPE_SUMMARY_CHROMS
result_file_content, result_file_name = octopod_client.result_api.download_result_file(
  order_id=order_id, 
  result_type=result_type,
)
```

# Octopod CLI

A command-line interface for automating file processing with the GalateaBio API.

## Features

- Automatic upload mode selection:
  - HTTP for files ≤ 50MB
  - SFTP for files > 50MB
- Optional reuse of existing files on server with `--check-if-file-exists`
- Handles file validation, order submission, and result downloads
- Automatic token refresh and re-authentication
- Configurable polling intervals and timeouts

## Installation

Requires Python 3.6+ and the following packages:

- requests
- paramiko

You can install the required packages using pip:

```bash
pip install requests paramiko
```

## Usage

### Basic Example

```bash
python octopod-cli.py \
    --username "user@example.com" \
    --password "your_password" \
    --file_to_process "data.vcf" \
    --model "skywalker" \
    --download_folder "results" \
    --check-if-file-exists
```

### Arguments

- `--username`: Your GalateaBio account email.
- `--password`: Your GalateaBio account password.
- `--file_to_process`: Path to the VCF file to be processed.
- `--model`: The model to use for processing (e.g., "skywalker").
- `--download_folder`: Directory where results will be saved.
- `--check-if-file-exists`: (Optional) Reuse existing files on the server if they already exist.
- `--poll-interval`: Polling interval in seconds for checking job status.
- `--timeout`: Maximum time in seconds to wait for job completion.

### Advanced Usage

- **Configuring Polling Intervals and Timeouts**:

  To adjust how frequently the CLI checks for job status and set a timeout:

  ```bash
  python octopod-cli.py \
      --username "user@example.com" \
      --password "your_password" \
      --file_to_process "data.vcf" \
      --model "skywalker" \
      --download_folder "results" \
      --poll-interval 30 \
      --timeout 600
  ```

## Logging

The CLI provides detailed logs of its operations. Logs are output to the console and can be redirected to a file:

```bash
python octopod-cli.py [options] > octopod.log 2>&1
```

## Troubleshooting

- **Authentication Errors**: Ensure your username and password are correct.
- **File Upload Issues**: Check your network connection and verify file size limits.
- **Dependency Issues**: Make sure all required packages are installed.
- **Permission Denied**: Ensure you have write permissions to the specified download folder.
