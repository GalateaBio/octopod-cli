from abc import ABC, abstractmethod
from typing import Any

from octopod_cli import get_config
from octopod_cli.utils import API_MODE_API_KEY, API_MODE_USERNAME_PASSWORD
from octopod_wrapper import OctopodClient


class BaseCommand(ABC):
    _command_parser: Any

    @property
    def command_parser(self):
        if not self._command_parser:
            raise Exception('command parser not set')
        return self._command_parser

    @property
    @abstractmethod
    def command_name(self) -> str:
        raise NotImplemented

    @abstractmethod
    def add_args(self, subparsers, parser):
        raise NotImplemented

    @abstractmethod
    def run_command(self, args):
        raise NotImplemented

    def __str__(self) -> str:
        return self.command_name


class BaseApiCommand(BaseCommand, ABC):
    @abstractmethod
    def _run_command_logic(self, args, api_client: OctopodClient):
        raise NotImplemented

    def run_command(self, args):
        config = get_config()
        if config is None:
            return

        if not config.api_base_url:
            print(
                'ERROR! api_base_url not configured. '
                'Please use set-config command with correct arguments'
            )
            return

        if config.api_mode == API_MODE_API_KEY and not config.api_key:
            print(
                'ERROR! api_key not configured for api_mode=1. '
                'Please use set-config command with correct arguments'
            )
            return

        if config.api_mode == API_MODE_USERNAME_PASSWORD and not config.api_username or not config.api_password:
            print(
                'ERROR! api_username or api_password not configured for api_mode=2. '
                'Please use set-config command with correct arguments'
            )
            return

        api_key = config.api_key
        if config.api_mode == API_MODE_USERNAME_PASSWORD:
            auth_json = OctopodClient.authenticate(
                username=config.api_username,
                password=config.api_password,
                base_url=config.api_base_url,
            )
            api_key = auth_json.get('access', api_key)

        octopod_client = OctopodClient(base_url=config.api_base_url, api_key=api_key)
        self._run_command_logic(args, octopod_client)
