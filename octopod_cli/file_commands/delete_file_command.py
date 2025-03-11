from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class DeleteFileCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'delete-file'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Delete file via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--file_id',
            required=True,
            help='File ID',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        api_client.file_api.delete_file(args.file_id)
        print('Deleted.')
