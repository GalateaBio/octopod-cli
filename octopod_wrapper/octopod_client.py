from octopod_wrapper import OctopodException
from octopod_wrapper.api.file_api import _FileApi
from octopod_wrapper.api.order_api import _OrderApi
from octopod_wrapper.api.organization_api import _OrganizationApi
from octopod_wrapper.api.tag_api import _TagApi


class OctopodClient:
    file_api: _FileApi
    order_api: _OrderApi
    organization_api: _OrganizationApi
    tag_api: _TagApi

    def __init__(self, base_url: str, api_key: str) -> None:
        super().__init__()
        if not api_key:
            raise OctopodException('Api key is empty')
        if not base_url:
            raise OctopodException('Base Octopod URL is empty')
        self.file_api = _FileApi(base_url=base_url, api_key=api_key)
        self.order_api = _OrderApi(base_url=base_url, api_key=api_key)
        self.organization_api = _OrganizationApi(base_url=base_url, api_key=api_key)
        self.tag_api = _TagApi(base_url=base_url, api_key=api_key)
