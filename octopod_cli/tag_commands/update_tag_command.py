import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class UpdateTagCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'update-tag'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Update tag via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--tag_id',
            required=True,
            help='Tag ID',
            type=str,
        )
        self._command_parser.add_argument(
            '--name',
            required=True,
            help='Tag name',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        result = api_client.tag_api.update_tag(tag_id=args.tag_id, new_name=args.name)
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
