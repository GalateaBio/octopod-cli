import json
import os.path

from octopod_cli import BaseApiCommand, get_config
from octopod_wrapper import OctopodClient


class DownloadResultJsonCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'download-result-json'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Download result json via API')
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

    def _run_command_logic(self, args, api_client: OctopodClient):
        result = api_client.result_api.download_result_json(order_id=args.order_id, result_type=args.result_type)
        config = get_config()

        file_name = f'{args.order_id}_{args.result_type}.json'
        if config.download_folder:
            file_name = os.path.join(config.download_folder, file_name)

        with open(file_name, 'w') as f:
            json.dump(result, f, indent=4)
            print(f'Result json file saved as {file_name}')
