from typing import Union, List, Optional, Dict
from uuid import UUID

import requests

from octopod_wrapper import OctopodException
from octopod_wrapper.api import _BaseApi


class _OrderApi(_BaseApi):
    def submit_order(
        self,
        source_file_id: Union[str, UUID],
        model_name: str,
        tags_ids: Optional[List[Union[str, UUID]]] = None,
    ) -> Optional[Dict]:
        source_file_id = self.convert_str_to_uuid(source_file_id)

        if tags_ids is None:
            tags_ids = []

        str_tags_ids: List[str] = []
        for tag_id in tags_ids:
            if isinstance(tag_id, str):
                tag_id = self.convert_str_to_uuid(tag_id)

            if tag_id is None:
                raise OctopodException('Wrong uuid format of tag id')
            str_tags_ids.append(str(tag_id))

        payload = {
            'source_file_id': str(source_file_id),
            'model_name': model_name,
            'tags_ids': str_tags_ids,
        }

        response = self._make_api_call(requests.post, 'exec/orders', json=payload)
        response_data = response.json()
        if len(response_data) == 0:
            return None
        return response_data[0]

    def list_orders(self, **kwargs) -> Dict:
        """
            List orders with possible filters.

            Keyword Args:
                page: Requested page number. Should be int.
                filter: Order id or file id or file name. Should be str or uuid4.
                tags_ids: List of tags ids. Each item should be in uuid4 format.
                status: Order status. Possible values: Submitted, Running, Completed, Failed, Canceled,
                        Model completed, Making report, Collecting report results, Reports failed.
                type: Type of file. Possible values: GNT, WGS, EXTERNAL.
                model_name: Model name.
                model_api_name: Model api name.
                status_group: Status group. Possible values: initializing, running, completed, failed.
                min_date: Min started date. Should be in format YYYY-MM-DD.
                max_date: Max started date. Should be in format YYYY-MM-DD.

            Returns:
                Dict: Pagination object with list of order objects.
        """
        if kwargs is None:
            kwargs = {}
        query_params = self._add_pagination_query_params(kwargs)

        response = self._make_api_call(requests.get, 'exec/orders', params=query_params)
        return response.json()

    def find_order_by_id_or_file_id(self, order_id_or_file_id: Union[str, UUID]) -> Optional[Dict]:
        """
            List orders with possible filters.

            Args:
                order_id_or_file_id: Order id or file id.

            Returns:
                Dict: Pagination object with list of order objects.
        """
        order_id_or_file_id = self.convert_str_to_uuid(order_id_or_file_id)

        query_params = {'filter': str(order_id_or_file_id)}
        query_params = self._add_pagination_query_params(query_params)

        response = self._make_api_call(requests.get, 'exec/orders', params=query_params)
        response_data: Dict = response.json()
        if response_data.get('count', 0) == 0:
            return None
        return response_data['results'][0]
