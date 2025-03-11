import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class ListResultSamplesCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'list-result-samples'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='List result samples via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--order_id',
            required=True,
            help='Order ID',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        result = api_client.result_api.list_result_samples(args.order_id)
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
