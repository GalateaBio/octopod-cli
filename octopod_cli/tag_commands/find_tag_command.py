import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class FindTagCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'find-tag'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Find tag by id via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--tag_id',
            required=True,
            help='Tag ID',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        result = api_client.tag_api.get_tag_by_id(args.tag_id)
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
