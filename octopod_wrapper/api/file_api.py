import re
from io import FileIO, BytesIO
from typing import Union, Optional, Dict, BinaryIO, Tuple
from uuid import UUID

import requests

from octopod_wrapper.api import _BaseApi


class _FileApi(_BaseApi):
    def download_file(self, file_id: Union[str, UUID]) -> Tuple[BytesIO, Optional[str]]:
        """
            Download file.

            Args:
                file_id: File id. Should be in uuid4 format.

            Returns:
                Tuple[BytesIO, Optional[str]]: File object and file name.
        """
        file_id = self.convert_str_to_uuid(file_id)

        response = self._make_api_call(requests.get, f'data/files/{str(file_id)}/download')
        file_name: Optional[str] = None
        content_disposition = response.headers.get('content-disposition', None)
        if content_disposition:
            search_result = re.search('filename="(.+?)"', str(content_disposition))
            if search_result:
                file_name = search_result.group(1)
        return BytesIO(response.content), file_name

    def upload_file_from_file(self, file_name: str) -> Dict:
        """
            Upload a local file.

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
            Uploads in memory file.

            Args:
                file_content: File content.
                file_name: File name.

            Returns:
                Dict: The newly created file object.
        """
        response = self._make_api_call(requests.post, 'data/files/upload', files={'file': (file_name, file_content)})
        return response.json()

    def find_file_by_id(self, file_id: Union[str, UUID]) -> Optional[Dict]:
        """
            Find file by id.

            Args:
                file_id: File Id. Should be in uuid4 format.

            Returns:
                Optional[Dict]: File object or None if file not found.
        """
        file_id = self.convert_str_to_uuid(file_id)

        query_params = {'file': str(file_id)}
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
                min_date: Min uploaded date. Should be str in format YYYY-MM-DD.
                max_date: Max uploaded date. Should be str in format YYYY-MM-DD.
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

    def delete_file(self, file_id: Union[str, UUID]):
        """
            Delete file by id.

            Args:
                file_id: File Id. Should be in uuid4 format.
        """
        file_id = self.convert_str_to_uuid(file_id)
        self._make_api_call(requests.delete, f'data/files/{str(file_id)}')

    def update_file_sample_alias(self, file_id: Union[str, UUID], new_sample_alias: str) -> Dict:
        """
            Update file wit new sample alias.

            Args:
                file_id: File Id. Should be in uuid4 format.
                new_sample_alias: New sample alias.

            Returns:
                Dict: File object.
        """
        file_id = self.convert_str_to_uuid(file_id)

        response = self._make_api_call(
            requests.put,
            f'data/files/{str(file_id)}',
            json={'sample_alias': new_sample_alias},
        )
        return response.json()
