from typing import Union, List, Optional, Dict, Any
from uuid import UUID

import requests

from octopod_wrapper import OctopodException
from octopod_wrapper.api import _BaseApi


class _OrderApi(_BaseApi):
    ORDER_STATUS_REGISTERED = 'Registered'
    ORDER_STATUS_PREPARING = 'Preparing'
    ORDER_STATUS_SUBMITTED = 'Submitted'
    ORDER_STATUS_RUNNING = 'Running'
    ORDER_STATUS_MODEL_COMPLETED = 'Model completed'
    ORDER_STATUS_COMPLETED = 'Completed'
    ORDER_STATUS_FAILED = 'Failed'
    ORDER_STATUS_CANCELED = 'Canceled'
    ORDER_STATUS_CANCELING = 'Canceling'
    ORDER_STATUS_MAKING_REPORT = 'Making report'
    ORDER_STATUS_COLLECT_REPORT_RESULT = 'Collecting report results'
    ORDER_STATUS_REPORTS_FAILED = 'Reports failed'
    ORDER_STATUS_QC_FAILED = 'QC failed'

    ORDER_TYPE_GNT = 'GNT'
    ORDER_TYPE_WGS = 'WGS'
    ORDER_TYPE_EXTERNAL = 'EXTERNAL'

    ORDER_STATUS_GROUP_INITIALIZING = 'initializing'
    ORDER_STATUS_GROUP_RUNNING = 'running'
    ORDER_STATUS_GROUP_COMPLETED = 'completed'
    ORDER_STATUS_GROUP_FAILED = 'failed'

    def cancel_order(self, order_id: Union[str, UUID]):
        """
            Cancel order execution.

            Args:
                order_id: Order id. Should be in uuid4 format.
        """
        order_id = self.convert_str_to_uuid(order_id)

        self._make_api_call(
            requests.post,
            f'exec/cancel',
            json={'order_id': str(order_id)},
        )

    def update_order_tags(
        self,
        order_id: Union[str, UUID],
        tags_ids: Optional[List[Union[str, UUID]]] = None,
    ) -> Dict:
        """
            Update order's tags.

            Args:
                order_id: Order id. Should be in uuid4 format.
                tags_ids: List of tags ids. Each item should be in uuid4 format.

            Returns:
                Dict: Order object.
        """
        order_id = self.convert_str_to_uuid(order_id)

        if tags_ids is None:
            tags_ids = []

        str_tags_ids: List[str] = []
        for tag_id in tags_ids:
            if isinstance(tag_id, str):
                tag_id = self.convert_str_to_uuid(tag_id)

            if tag_id is None:
                raise OctopodException('Wrong uuid format of tag id')
            str_tags_ids.append(str(tag_id))

        response = self._make_api_call(
            requests.patch,
            f'exec/orders/{str(order_id)}',
            json={'tags_ids': str_tags_ids},
        )
        return response.json()

    def submit_order(
        self,
        file_id: Union[str, UUID],
        model_name: str,
        tags_ids: Optional[List[Union[str, UUID]]] = None,
        pdf_report_types: Optional[List[str]] = None,
        pdf_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict]:
        """
            Submit order.

            Args:
                file_id: File id. Should be in uuid4 format.
                model_name: Model name.
                tags_ids: List of tags ids. Each item should be in uuid4 format.
                pdf_report_types: List of PDF report types for Mysterio model. Available values: "PRS_CLINICAL_CARDIO", "PRS_CLINICAL_CANCER", "PRS_RUO_CARDIO", "PRS_RUO_CANCER"
                pdf_metadata: Dict of pdf metadata parameters.
            Returns:
                Dict: Order object.
        """
        file_id = self.convert_str_to_uuid(file_id)

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
            'source_file_id': str(file_id),
            'model_name': model_name,
            'tags_ids': str_tags_ids,
            'pdf_report_types': pdf_report_types,
            'pdf_metadata': pdf_metadata,
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
                status: Order status. Should be str. Possible values:
                    ORDER_STATUS_REGISTERED, ORDER_STATUS_PREPARING,
                    ORDER_STATUS_SUBMITTED, ORDER_STATUS_RUNNING,
                    ORDER_STATUS_MODEL_COMPLETED, ORDER_STATUS_COMPLETED,
                    ORDER_STATUS_FAILED, ORDER_STATUS_CANCELED,
                    ORDER_STATUS_CANCELING, ORDER_STATUS_MAKING_REPORT,
                    ORDER_STATUS_COLLECT_REPORT_RESULT, ORDER_STATUS_REPORTS_FAILED,
                    ORDER_STATUS_QC_FAILED.
                type: Type of file. Should be str. Possible values: ORDER_TYPE_GNT, ORDER_TYPE_WGS, ORDER_TYPE_EXTERNAL.
                model_name: Model name. Should be str.
                model_api_name: Model api name. Should be str.
                status_group: Status group. Should be str. Possible values:
                    ORDER_STATUS_GROUP_INITIALIZING,
                    ORDER_STATUS_GROUP_RUNNING,
                    ORDER_STATUS_GROUP_COMPLETED,
                    ORDER_STATUS_GROUP_FAILED
                min_date: Min started date. Should be str in format YYYY-MM-DD.
                max_date: Max started date. Should be str in format YYYY-MM-DD.

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
                order_id_or_file_id: Order id or file id. Should be in uuid4 format.

            Returns:
                Optional[Dict]: Pagination object with list of order objects.
        """
        order_id_or_file_id = self.convert_str_to_uuid(order_id_or_file_id)

        query_params = {'filter': str(order_id_or_file_id)}
        query_params = self._add_pagination_query_params(query_params)

        response = self._make_api_call(requests.get, 'exec/orders', params=query_params)
        response_data: Dict = response.json()
        if response_data.get('count', 0) == 0:
            return None
        return response_data['results'][0]
