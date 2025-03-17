import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class FindFileCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'find-file'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Find file via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--file_id',
            nargs='?',
            default=None,
            help='File ID',
            type=str,
        )
        self._command_parser.add_argument(
            '--file_name',
            nargs='?',
            default=None,
            help='File name',
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
        if not args.file_id and not args.file_name:
            return

        if args.file_id:
            result = api_client.file_api.find_file_by_id(args.file_id)
            json_obj = json.dumps(result, indent=4)
            print(json_obj)
            return

        kwargs = {'file': args.file_name}
        if args.page:
            kwargs['page'] = args.page

        result = api_client.file_api.list_files(**kwargs)
        result.pop('next')
        result.pop('previous')
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
