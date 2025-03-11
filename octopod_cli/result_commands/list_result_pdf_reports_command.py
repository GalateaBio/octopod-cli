import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class ListResultPdfReportsCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'list-result-pdf-reports'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='List result PDF reports via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--order_id',
            required=True,
            help='Order ID',
            type=str,
        )
        self._command_parser.add_argument(
            '--request_version',
            nargs='?',
            default=None,
            help='Filter by request version',
            type=str,
        )
        self._command_parser.add_argument(
            '--report_version',
            nargs='?',
            default=None,
            help='Filter by report version',
            type=str,
        )
        self._command_parser.add_argument(
            '--sample_id',
            nargs='?',
            default=None,
            help='Filter by sample ID',
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
        if args.request_version:
            kwargs['request_version'] = args.request_version
        if args.report_version:
            kwargs['report_version'] = args.report_version
        if args.sample_id:
            kwargs['sample_id'] = args.sample_id
        if args.page:
            kwargs['page'] = args.page
        result = api_client.result_api.list_pdf_reports(order_id=args.order_id, **kwargs)
        result.pop('next')
        result.pop('previous')
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
