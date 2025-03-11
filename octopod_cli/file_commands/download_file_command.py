import os.path

from octopod_cli import BaseApiCommand, get_config
from octopod_wrapper import OctopodClient


class DownloadFileCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'download-file'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Download file via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--file_id',
            required=True,
            help='File ID',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        file_content, file_name = api_client.file_api.download_file(args.file_id)
        config = get_config()

        if config.download_folder:
            file_name = os.path.join(config.download_folder, file_name)

        with open(file_name, 'wb') as f:
            f.write(file_content.getbuffer().tobytes())
            print(f'File saved as {file_name}')
