from typing import Dict

import requests

from octopod_wrapper import OctopodException
from octopod_wrapper.api import _BaseApi


class _OrganizationApi(_BaseApi):
    def get_organization_info(self) -> Dict:
        """
            Get organization information.

            Returns:
                Dict: Object with organization's information.
        """
        response = self._make_api_call(requests.get, 'users/me')
        response_data: Dict = response.json()
        org_info = response_data.get('org', None)
        if org_info is None:
            raise OctopodException('Failed to get organization information')
        return org_info
