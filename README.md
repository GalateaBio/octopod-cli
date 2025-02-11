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
