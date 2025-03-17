from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class CancelOrderCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'cancel-order'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Cancel order via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--order_id',
            required=True,
            help='Order ID',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        api_client.order_api.cancel_order(args.order_id)
        print('Canceled.')
