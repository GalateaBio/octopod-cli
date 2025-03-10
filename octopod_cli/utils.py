import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

config_file_name = 'config.txt'


@dataclass
class Config:
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    sftp_host: Optional[str] = None
    sftp_user: Optional[str] = None
    sftp_keyfile: Optional[str] = None


def get_config() -> Optional[Config]:
    config_file = Path('config.txt')
    if not config_file.exists():
        print('Config not set. Please use config command to set config')
        return None
    with open('config.txt', 'r') as file:
        config = Config()
        fields = dataclasses.fields(config)
        lines = [line.strip() for line in file]
        for line in lines:
            for field in fields:
                if line.startswith(field.name):
                    setattr(config, field.name, line.replace(f'{field.name}=', ''))

        return config
