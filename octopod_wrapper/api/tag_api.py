from typing import Dict, Union
from uuid import UUID

import requests

from octopod_wrapper import OctopodException
from octopod_wrapper.api import _BaseApi


class _TagApi(_BaseApi):
    def list_tags(self, **kwargs) -> Dict:
        """
            List tags with possible filtering by tag name.

            Keyword Args:
                page: Requested page number. Should be int.
                name: Tag name to filtering. Should be str.

            Returns:
                Dict: Pagination object with list of tag objects.
        """

        if kwargs is None:
            kwargs = {}
        query_params = self._add_pagination_query_params(kwargs)

        response = self._make_api_call(requests.get, 'exec/tags', params=query_params)
        return response.json()

    def create_tag(self, name: str) -> Dict:
        """
            Create new tag.

            Args:
                name: Tag name.

            Returns:
                Dict: Newly created tag object.
        """
        if not name:
            raise OctopodException('Name of tag is empty')

        payload = {'name': name}

        response = self._make_api_call(requests.post, 'exec/tags', json=payload)
        return response.json()

    def get_tag_by_id(self, tag_id: Union[str, UUID]) -> Dict:
        """
            Find tag by id.

            Args:
                tag_id: Tag Id. Should be in uuid4 format.

            Returns:
                Dict: Tag object.
        """
        tag_id = self.convert_str_to_uuid(tag_id)

        response = self._make_api_call(requests.get, f'exec/tags/{str(tag_id)}')
        return response.json()

    def delete_tag(self, tag_id: Union[str, UUID]):
        """
            Delete tag by id.

            Args:
                tag_id: Tag Id. Should be in uuid4 format.
        """
        tag_id = self.convert_str_to_uuid(tag_id)

        self._make_api_call(requests.delete, f'exec/tags/{str(tag_id)}')

    def update_tag(self, tag_id: Union[str, UUID], new_name: str) -> Dict:
        """
            Update tag with new name.

            Args:
                tag_id: Tag Id. Should be in uuid4 format.
                new_name: New tag name.
        """
        tag_id = self.convert_str_to_uuid(tag_id)

        if not new_name:
            raise OctopodException('Name of tag is empty')

        payload = {'name': new_name}

        response = self._make_api_call(requests.put, f'exec/tags/{str(tag_id)}', json=payload)
        return response.json()
