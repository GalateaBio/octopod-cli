import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class ListTagsCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'list-tags'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='List tags via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--name',
            nargs='?',
            default=None,
            help='Filter by tag name',
            type=str,
        )
        self._command_parser.add_argument(
            '--page',
            nargs='?',
            default=None,
            help='Page',
            type=int,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        kwargs = {}
        if args.name:
            kwargs['name'] = args.name
        if args.page:
            kwargs['page'] = args.page

        result = api_client.tag_api.list_tags(**kwargs)
        result.pop('next')
        result.pop('previous')
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
