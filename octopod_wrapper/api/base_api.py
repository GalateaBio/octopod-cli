from abc import ABC
from typing import Dict, Union
from uuid import UUID

import requests

from octopod_wrapper import OctopodException, convert_str_to_uuid


class _BaseApi(ABC):
    _base_url: str
    _api_key: str

    def __init__(self, base_url: str, api_key: str) -> None:
        super().__init__()
        self._base_url = base_url
        self._api_key = api_key

    @staticmethod
    def convert_str_to_uuid(uuid_val: Union[str, UUID]) -> UUID:
        if isinstance(uuid_val, str):
            uuid_val = convert_str_to_uuid(uuid_val)

        if uuid_val is None:
            raise OctopodException('Wrong uuid format')
        return uuid_val

    @staticmethod
    def _add_pagination_query_params(query_params: Dict) -> Dict:
        if query_params.get('page', None) is None:
            query_params['page'] = 1
        query_params['page_size'] = 10
        return query_params

    def _make_api_call(self, func, endpoint_path: str, **kwargs) -> requests.Response:
        headers = kwargs.get('headers', None)
        if headers is None:
            kwargs['headers'] = {}
        kwargs['headers']['Authorization'] = f'Bearer {self._api_key}'
        kwargs['headers']['Accept'] = 'application/json'

        response: requests.Response = func(f'{self._base_url}/api/v1/{endpoint_path}', **kwargs)
        response.raise_for_status()
        return response
