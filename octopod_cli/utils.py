import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

config_file_name = 'config.txt'

API_MODE_API_KEY = 1
API_MODE_USERNAME_PASSWORD = 2


@dataclass
class Config:
    api_mode: int = API_MODE_API_KEY
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    api_username: Optional[str] = None
    api_password: Optional[str] = None
    sftp_host: Optional[str] = None
    sftp_user: Optional[str] = None
    sftp_keyfile_path: Optional[str] = None
    download_folder: Optional[str] = None


def get_config() -> Optional[Config]:
    config_file = Path('config.txt')
    if not config_file.exists():
        print('ERROR! Config not set. Please use config command to set config')
        return None
    with open('config.txt', 'r') as file:
        config = Config()
        fields = dataclasses.fields(config)
        lines = [line.strip() for line in file]
        for line in lines:
            for field in fields:
                if line.startswith(field.name):
                    val = line.replace(f'{field.name}=', '')
                    if isinstance(field.type, type(int)):
                        setattr(config, field.name, int(val))
                    else:
                        setattr(config, field.name, val)

        return config
