import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class FindOrderCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'find-order'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Find order via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--order_id_or_file_id',
            required=True,
            help='Order ID or File ID',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        result = api_client.order_api.find_order_by_id_or_file_id(args.order_id_or_file_id)
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
