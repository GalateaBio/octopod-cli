from typing import Dict

import requests

from octopod_wrapper import OctopodException
from octopod_wrapper.api import _ResultApi
from octopod_wrapper.api import _FileApi
from octopod_wrapper.api import _OrderApi
from octopod_wrapper.api import _OrganizationApi
from octopod_wrapper.api import _TagApi


class OctopodClient:
    file_api: _FileApi
    order_api: _OrderApi
    organization_api: _OrganizationApi
    tag_api: _TagApi
    result_api: _ResultApi

    def __init__(self, base_url: str, api_key: str) -> None:
        super().__init__()
        if not api_key:
            raise OctopodException('api_key arg is empty')
        if not base_url:
            raise OctopodException('base_url arg is empty')

        self.file_api = _FileApi(base_url=base_url, api_key=api_key)
        self.order_api = _OrderApi(base_url=base_url, api_key=api_key)
        self.organization_api = _OrganizationApi(base_url=base_url, api_key=api_key)
        self.tag_api = _TagApi(base_url=base_url, api_key=api_key)
        self.result_api = _ResultApi(base_url=base_url, api_key=api_key)

    @staticmethod
    def authenticate(username: str, password: str, base_url: str) -> Dict:
        payload = {
            'email': username,
            'password': password,
        }
        response: requests.Response = requests.post(f'{base_url}/api/v1/users/auth', json=payload)
        response.raise_for_status()
        return response.json()
