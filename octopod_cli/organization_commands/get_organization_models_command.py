import json

from octopod_cli import BaseApiCommand
from octopod_wrapper import OctopodClient


class GetOrganizationModelsCommand(BaseApiCommand):
    @property
    def command_name(self) -> str:
        return 'get-organization-models'

    def add_args(self, subparsers, parser):
        self._command_parser = subparsers.add_parser(self.command_name, help='Get organization models via API')
        self._command_parser.set_defaults(command=self.command_name)
        self._command_parser.add_argument(
            '--org_id',
            required=True,
            help='Organization ID',
            type=str,
        )

    def _run_command_logic(self, args, api_client: OctopodClient):
        result = api_client.organization_api.get_organization_models(args.org_id)
        json_obj = json.dumps(result, indent=4)
        print(json_obj)
