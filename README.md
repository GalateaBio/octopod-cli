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
## Basic usage
```sh
octopod-cli -h  # to show available commands

#Configure first
octopod-cli set-config --api_key="<api_key>" --api_base_url="<api_base_url>" --sftp_host="<sftp_host>" --sftp_user="<sftp_user>" --sftp_keyfile="<sftp_keyfile>" --download_folder="<download_folder>"
octopod-cli get-config  # to show current config

octopod-cli api-upload-file -h  # to show help of selected command
octopod-cli api-upload-file --file_name="<full_file_name>"  # to upload file
octopod-cli find-file --file_id="<file_id>"  # to find file by id
octopod-cli find-file --file_name="<file_name>"  # to find files by name
octopod-cli get-organization-info  # to show organization info with available models
octopod-cli submit-order --file_id="<file_id>" --model="<model_name>"  # submit order
octopod-cli find-order --order_id_or_file_id="<order_id_or_file_id>"  # find order by order id or file id
octopod-cli download-result-file --order_id="<order_id>" --result_type="SUMMARY_SUPERSET"  # download order result by type
```
