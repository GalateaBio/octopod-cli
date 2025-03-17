import os.path

from octopod_cli import BaseApiCommand, get_config
from octopod_wrapper import OctopodClient


class DownloadResultFileCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'download-result-file'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Download result file via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--order_id',
            required=True,
            help='Order ID',
            type=str,
        )
        self._command_parser.add_argument(
            '--result_type',
            required=True,
            help='Result type',
            type=str,
        )
        self._command_parser.add_argument(
            '--pdf_request_id',
            nargs='?',
            default=None,
            help='PDF report request id',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        kwargs = {}
        if args.pdf_request_id:
            kwargs['pdf_request_id'] = args.pdf_request_id
        file_content, file_name = api_client.result_api.download_result_file(
            order_id=args.order_id,
            result_type=args.result_type,
            **kwargs,
        )
        config = get_config()

        if config.download_folder:
            file_name = os.path.join(config.download_folder, file_name)

        with open(file_name, 'wb') as f:
            f.write(file_content.getbuffer().tobytes())
            print(f'Result file saved as {file_name}')
