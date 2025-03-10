import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class UploadFileViaApiCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'api-upload-file'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, parents=[parser], help='Upload file via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--file_name',
            required=True,
            help='Full path to the file to upload',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        result = api_client.file_api.upload_file(args.file_name)
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
