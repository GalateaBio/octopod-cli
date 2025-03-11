import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class UpdateOrderTagsCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'update-order-tags'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Update order tags via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--order_id',
            required=True,
            help='Order ID',
            type=str,
        )
        self._command_parser.add_argument(
            '--tags_ids',
            nargs='?',
            default=None,
            help='List of tags ids delimited by comma',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        tags_ids = None
        if args.tags_ids:
            tags_ids = [item.strip() for item in args.tags_ids.split(',')]
        result = api_client.order_api.update_order_tags(order_id=args.order_id, tags_ids=tags_ids)
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
