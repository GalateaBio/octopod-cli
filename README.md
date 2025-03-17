# Octopod wrapper & CLI tool
Library to work with GalateaBio API via python or via CLI tool.

## Supported features:
* File uploading via API and SFTP
* File deletion
* Get organization's information and available models
* Searching files
* Submitting orders
* Cancelling orders
* Searching/adding/editing tags
* Downloading order's results


## Installation
### Via pip from PyPI
```sh
pip install octopod
```

### Local Installation
```sh
git clone repository
```
In your project run 
```sh
pip install octopod file://<path_to_repo>
```


## Wrapper usage
### Create Octopod client
```python
base_url = 'Octopod API URL'  # Example https://<OCTOPOD_API_HOST>
api_key = 'Octopod API Key'

octopod_client = OctopodClient(base_url=base_url, api_key=api_key)
```

### Upload file
#### API upload. For files less than 50 mb
```python
file_obj = octopod_client.file_api.upload_file('my_file.zip')
```
or
```python
file_name = 'my_file.zip'
with open(file_name, "rb") as fh:
    buf = BytesIO(fh.read())
    file_obj = octopod_client.file_api.upload_file_from_io(buf, file_name)
```
#### SFTP upload. For files more than 50 mb
```python
sftp_keyfile = 'File name with Octopod SFTP private key'
sftp_octopod_client = OctopodSftpClient(
  sftp_host='Octopod SFTP host',
  sftp_user='Octopod SFTP user',
  sftp_password=None,
  sftp_keyfile=sftp_keyfile,
)
file_name = sftp_octopod_client.upload_file_from_file(
  file_name='my_file.zip',
  remote_filename='my_file.zip',
  remote_folder='my_awesome_folder_name',
)
```

### List files/get file information
```python
file_name = 'my_file.zip'
files_objs = octopod_client.file_api.list_files(**{'file': file_name})
if files_objs.get('count', 0) > 0:
    file_id = files_objs.get('results', [])[0].get('id')
    file_obj = octopod_client.file_api.find_file_by_id(file_id)
```

### Get organization's available models
```python
org_info = octopod_client.organization_api.get_organization_info()
available_model_names = org_info.get('available_models', [])
```

### Submit order
```python
file_id = 'my_file_id'
model_name = 'my_model_name'
order_obj = octopod_client.order_api.submit_order(file_id=file_id, model_name=model_name)
```

### Get order information
```python
order_id_or_file_id = 'my_order_id_or_file_id'
order_obj = octopod_client.order_api.find_order_by_id_or_file_id(order_id_or_file_id)
order_status = order_obj.get('status')
order_result_types = order_obj.get('result_types')
```

### Download order's result
```python
order_id = 'my_order_id'
result_type = octopod_client.result_api.RESULT_TYPE_SUMMARY_CHROMS  
# result_type = order_obj.get('result_types')[0]  # get result type from order info
result_file_content, result_file_name = octopod_client.result_api.download_result_file(
  order_id=order_id, 
  result_type=result_type,
)
```


## Octopod CLI usage
### Set/Get config options
```shell
octopod-cli set-config --api_key="<api_key>" --api_base_url="<api_base_url>" --sftp_host="<sftp_host>" --sftp_user="<sftp_user>" --sftp_keyfile="<sftp_keyfile>" --download_folder="<download_folder>"
```
```shell
octopod-cli get-config
```

### File upload
#### API upload. For files less than 50 mb
```shell
octopod-cli api-upload-file --file_name="<full_file_name>"
```
#### SFTP upload. For files more than 50 mb
```shell
octopod-cli sftp-upload-file --file_name="<full_file_name>"
```

### Get file information
```shell
octopod-cli find-file --file_id="<file_id>"
octopod-cli find-file --file_name="<file_name>"
```

### Get organization's available models
```shell
octopod-cli get-organization-info
```

### Submit order
```shell
octopod-cli submit-order --file_id="<file_id>" --model="<model_name>"
```

### Get order information
```shell
octopod-cli find-order --order_id_or_file_id="<order_id_or_file_id>"
```

### Download order's result
```shell
octopod-cli download-result-file --order_id="<order_id>" --result_type="SUMMARY_SUPERSET"
```
