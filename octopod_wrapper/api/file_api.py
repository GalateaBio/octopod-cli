from io import FileIO, BytesIO
from typing import Union, Optional, Dict, BinaryIO
from uuid import UUID

import requests

from octopod_wrapper.api import _BaseApi


class _FileApi(_BaseApi):
    def upload_file_from_file(self, file_name: str) -> Dict:
        """
            Uploads a local file and returns the new file object.

            Args:
                file_name: Path to the file to upload.

            Returns:
                Dict: The newly created file object.
        """
        with open(file_name, "rb") as f:
            response = self._make_api_call(requests.post, 'data/files/upload', files={'file': f})
            return response.json()

    def upload_file_from_io(self, file_content: Union[FileIO, BytesIO, BinaryIO], file_name: str) -> Dict:
        """
            Uploads in memory file and returns the new file object.

            Args:
                file_content: File content.
                file_name: File name.

            Returns:
                Dict: The newly created file object.
        """
        response = self._make_api_call(requests.post, 'data/files/upload', files={'file': (file_name, file_content)})
        return response.json()

    def find_file_by_id(self, id: Union[str, UUID]) -> Optional[Dict]:
        """
            Find file by id.

            Args:
                id: Id of file. Should be in uuid4 format.

            Returns:
                Optional[Dict]: File object or None if file not found.
        """
        id = self.convert_str_to_uuid(id)

        query_params = {'file': str(id)}
        query_params = self._add_pagination_query_params(query_params)

        response = self._make_api_call(requests.get, 'data/files', params=query_params)
        response_data: Dict = response.json()
        if response_data.get('count', 0) == 0:
            return None
        return response_data['results'][0]

    def list_files(self, **kwargs) -> Dict:
        """
            List files with possible filters.

            Keyword Args:
                page: Requested page number. Should be int.
                file: File id or file name. Should be str or uuid4.
                min_date: Min uploaded date. Should be in format YYYY-MM-DD.
                max_date: Max uploaded date. Should be in format YYYY-MM-DD.
                show_virtual: Fetch externally uploaded files. Should be boolean.
                only_acceptable: Fetch only acceptable files. Should be boolean.

            Returns:
                Dict: Pagination object with list of file objects.
        """
        if kwargs is None:
            kwargs = {}
        query_params = self._add_pagination_query_params(kwargs)

        response = self._make_api_call(requests.get, 'data/files', params=query_params)
        return response.json()
