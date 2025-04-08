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

Also wrapper supports authentication with username and password
```python
base_url = 'Octopod API URL'  # Example https://<OCTOPOD_API_HOST>
auth_json = OctopodClient.authenticate(
    username='my_username',
    password='my_password',
    base_url=base_url,
)
api_key = auth_json.get('access')  # fetched api_key has short lifetime!
octopod_client = OctopodClient(base_url=base_url, api_key=api_key)
```

### Upload file
#### API upload. Only for files less than 50 mb
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
#### SFTP upload. For any file size. (Preferable to use)
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
Submit order with PDF reports for Mysterio model
```python
file_id = 'my_file_id'
model_name = 'my_model_name'
pdf_report_types = ['PRS_RUO', 'PRS_CARDIO', 'PRS_CANCER']  # all possible PDF report types
order_obj = octopod_client.order_api.submit_order(
    file_id=file_id, 
    model_name=model_name, 
    pdf_report_types=pdf_report_types,
)
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
### Set config options
CLI tool supports 2 ways to communicate with API:
* Via API key. **api_mode=1**. Required parameters
* Via Username & password. **api_mode=2**. Required parameters **api_username**, **api_password**
```shell
octo set-config 
--api_mode=1
--api_key="<api_key>"
--api_username="<user_username>"
--api_password="user_password" 
--api_base_url="<api_base_url>" 
--sftp_host="<sftp_host>" 
--sftp_user="<sftp_user>" 
--sftp_keyfile="<sftp_keyfile>" 
--download_folder="<download_folder>"
```

### Get config options
```shell
octo get-config
```

### Clear config options
```shell
octo clear-config
```

### File upload
#### API upload. Only for files less than 50 mb
```shell
octo api-upload-file --file_name="<full_file_name>"
```
#### SFTP upload. For any file size. (Preferable to use)
```shell
octo sftp-upload-file --file_name="<full_file_name>"
```

### Get file information
```shell
octo find-file --file_id="<file_id>"
octo find-file --file_name="<file_name>"
```

### Get organization's available models
```shell
octo get-organization-info
```

### Submit order
```shell
octo submit-order --file_id="<file_id>" --model="<model_name>"
```
Submit order with PDF reports for Mysterio model
```shell
octo submit-order --file_id="<file_id>" --model="<model_name>" --pdf_report_types="PRS_RUO,PRS_CARDIO,PRS_CANCER"
```

### Get order information
```shell
octo find-order --order_id_or_file_id="<order_id_or_file_id>"
```

### Download order's result
```shell
octo download-result-file --order_id="<order_id>" --result_type="SUMMARY_SUPERSET"
```
