from pathlib import Path

from octopod_cli import BaseCommand, config_file_name


class GetConfigCommand(BaseCommand):
    @property
    def command_name(self) -> str:
        return 'get-config'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, parents=[parser], help='Get config')
        self._command_parser.set_defaults(command=self.command_name)

    def run_command(self, args):
        config_file = Path(config_file_name)
        if not config_file.exists():
            return
        with open('config.txt', 'r') as file:
            print('\nCurrent config:')
            for line in file:
                print(line.strip())
