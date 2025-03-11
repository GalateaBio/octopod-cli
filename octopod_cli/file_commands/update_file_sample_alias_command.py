import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class UpdateFileSampleAliasCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'update-file-sample-alias'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Update file sample alias via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--file_id',
            required=True,
            help='File ID',
            type=str,
        )
        self._command_parser.add_argument(
            '--sample_alias',
            required=True,
            help='New sample alias',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        result = api_client.file_api.update_file_sample_alias(args.file_id, args.sample_alias)
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
