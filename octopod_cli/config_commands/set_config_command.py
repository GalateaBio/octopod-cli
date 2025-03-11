from pathlib import Path
from typing import List

from octopod_cli import BaseCommand, config_file_name


class SetConfigCommand(BaseCommand):
    __arg_api_key = 'api_key'
    __arg_api_base_url = 'api_base_url'
    __arg_sftp_host = 'sftp_host'
    __arg_sftp_user = 'sftp_user'
    __arg_sftp_keyfile = 'sftp_keyfile'
    __arg_download_folder = 'download_folder'

    @property
    def command_name(self) -> str:
        return 'set-config'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Set config')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            f'--{self.__arg_api_key}',
            nargs='?',
            default=None,
            help='Octopod API key',
            type=str,
        )
        self._command_parser.add_argument(
            f'--{self.__arg_api_base_url}',
            nargs='?',
            default=None,
            help='Octopod API URL',
            type=str,
        )
        self._command_parser.add_argument(
            f'--{self.__arg_sftp_host}',
            nargs='?',
            default=None,
            help='Octopod SFTP host',
            type=str,
        )
        self._command_parser.add_argument(
            f'--{self.__arg_sftp_user}',
            nargs='?',
            default=None,
            help='Octopod SFTP user',
            type=str,
        )
        self._command_parser.add_argument(
            f'--{self.__arg_sftp_keyfile}',
            nargs='?',
            default=None,
            help='Octopod SFTP key file',
            type=str,
        )
        self._command_parser.add_argument(
            f'--{self.__arg_download_folder}',
            nargs='?',
            default=None,
            help='Folder to save files',
            type=str,
        )

    def run_command(self, args):
        new_api_key = getattr(args, self.__arg_api_key)
        new_api_base_url = getattr(args, self.__arg_api_base_url)
        new_sftp_host = getattr(args, self.__arg_sftp_host)
        new_sftp_user = getattr(args, self.__arg_sftp_user)
        new_sftp_keyfile = getattr(args, self.__arg_sftp_keyfile)
        new_download_folder = getattr(args, self.__arg_download_folder)

        config_file = Path(config_file_name)
        lines: List[str] = []
        if config_file.exists():
            with open(config_file_name, 'r') as file:
                lines = [line.strip() for line in file]

        with open(config_file_name, 'a') as file:
            new_lines = []

            self._fetch_config_value(
                lines=lines,
                result=new_lines,
                new_value=new_api_key,
                arg_name=self.__arg_api_key,
            )

            self._fetch_config_value(
                lines=lines,
                result=new_lines,
                new_value=new_api_base_url,
                arg_name=self.__arg_api_base_url,
            )

            self._fetch_config_value(
                lines=lines,
                result=new_lines,
                new_value=new_sftp_host,
                arg_name=self.__arg_sftp_host,
            )

            self._fetch_config_value(
                lines=lines,
                result=new_lines,
                new_value=new_sftp_user,
                arg_name=self.__arg_sftp_user,
            )

            self._fetch_config_value(
                lines=lines,
                result=new_lines,
                new_value=new_sftp_keyfile,
                arg_name=self.__arg_sftp_keyfile,
            )

            self._fetch_config_value(
                lines=lines,
                result=new_lines,
                new_value=new_download_folder,
                arg_name=self.__arg_download_folder,
            )

            file.truncate(0)
            file.write('\n'.join(new_lines))

            print('\nCurrent config:')
            print('\n'.join(new_lines))

    @staticmethod
    def _fetch_config_value(lines: List[str], result: List[str], new_value, arg_name):
        if new_value:
            result.append(f'{arg_name}={new_value}')
        else:
            existed_line = next((line for line in lines if line.startswith(arg_name)), None)
            if existed_line:
                result.append(existed_line)
