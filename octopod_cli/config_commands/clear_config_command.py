from pathlib import Path

from octopod_cli import BaseCommand, config_file_name


class ClearConfigCommand(BaseCommand):
    @property
    def command_name(self) -> str:
        return 'clear-config'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Clear config')
        self._command_parser.set_defaults(command=self.command_name)

    def run_command(self, args):
        config_file = Path(config_file_name)
        if not config_file.exists():
            return
        config_file.unlink()
        print('Done.')
