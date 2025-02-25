import re
from io import BytesIO
from typing import Union, Dict, Tuple, Optional
from uuid import UUID

import requests

from octopod_wrapper.api import _BaseApi


class _ResultApi(_BaseApi):
    RESULT_TYPE_SUMMARY_SUPERSET = 'SUMMARY_SUPERSET'
    RESULT_TYPE_SUMMARY_CHROMS = 'SUMMARY_CHROMS'
    RESULT_TYPE_DETAILED_SUPERSET = 'DETAILED_SUPERSET'
    RESULT_TYPE_DETAILED_CHROMS = 'DETAILED_CHROMS'
    RESULT_TYPE_WHOLE_RESULT = 'WHOLE_RESULT'
    RESULT_TYPE_CHROMS_SVG = 'CHROMS_SVG'
    RESULT_TYPE_PDF_REPORT = 'PDF_REPORT'
    RESULT_TYPE_PRS_DATA = 'PRS_DATA'
    RESULT_TYPE_PRS_TECH_DATA = 'PRS_TECH_DATA'
    RESULT_TYPE_PRS_QC = 'PRS_QC'
    RESULT_TYPE_EXEC_ERRORS = 'EXEC_ERRORS'
    RESULT_TYPE_UNKNOWN = 'UNKNOWN'

    def list_pdf_reports(self, order_id: Union[str, UUID], **kwargs) -> Dict:
        """
            List order's result PDF reports with possible filtering.

            Args:
                order_id: Order id. Should be in uuid4 format.

            Keyword Args:
                page: Requested page number. Should be int.
                request_version: Report request version. Should be int.
                report_version: Report version. Should be str.
                sample_id: Sample id. Should be str.

            Returns:
                Dict: Pagination object with list of pdf report objects.
        """
        order_id = self.convert_str_to_uuid(order_id)

        if kwargs is None:
            kwargs = {}
        query_params = self._add_pagination_query_params(kwargs)

        response = self._make_api_call(requests.get, f'data/results/{str(order_id)}/pdf_report', params=query_params)
        return response.json()

    def download_result_file(
        self,
        order_id: Union[str, UUID],
        result_type: str,
        **kwargs,
    ) -> Tuple[BytesIO, Optional[str]]:
        """
            Download order's result file by result type.

            Args:
                order_id: Order id. Should be in uuid4 format.
                result_type: Result type. Should be str. Possible values: RESULT_TYPE_SUMMARY_SUPERSET,
                                                                  RESULT_TYPE_SUMMARY_CHROMS,
                                                                  RESULT_TYPE_DETAILED_SUPERSET,
                                                                  RESULT_TYPE_DETAILED_CHROMS,
                                                                  RESULT_TYPE_WHOLE_RESULT,
                                                                  RESULT_TYPE_CHROMS_SVG,
                                                                  RESULT_TYPE_PDF_REPORT,
                                                                  RESULT_TYPE_PRS_DATA,
                                                                  RESULT_TYPE_PRS_TECH_DATA,
                                                                  RESULT_TYPE_PRS_QC,
                                                                  RESULT_TYPE_EXEC_ERRORS,
                                                                  RESULT_TYPE_UNKNOWN.

            Keyword Args:
                pdf_request_id: PDF report request id. Should be in uuid4 format.

            Returns:
                Tuple[BytesIO, Optional[str]]: File object and file name.
        """
        order_id = self.convert_str_to_uuid(order_id)

        if kwargs is None:
            kwargs = {}
        kwargs['result_type'] = result_type

        response = self._make_api_call(requests.get, f'data/results/{str(order_id)}/download', params=kwargs)
        file_name: Optional[str] = None
        content_disposition = response.headers.get('content-disposition', None)
        if content_disposition:
            search_result = re.search('filename="(.+?)"', str(content_disposition))
            if search_result:
                file_name = search_result.group(1)
        return BytesIO(response.content), file_name

    def download_result_json(self, order_id: Union[str, UUID], result_type: str) -> Dict:
        """
            Download order's result json by result type.

            Args:
                order_id: Order id. Should be in uuid4 format.
                result_type: Result type. Should be str. Possible values: RESULT_TYPE_SUMMARY_SUPERSET,
                                                                  RESULT_TYPE_SUMMARY_CHROMS,
                                                                  RESULT_TYPE_DETAILED_SUPERSET,
                                                                  RESULT_TYPE_DETAILED_CHROMS.

            Returns:
                Dict: Order result json data.
        """
        order_id = self.convert_str_to_uuid(order_id)

        response = self._make_api_call(
            requests.get,
            f'data/results/{str(order_id)}/json',
            params={'result_type': result_type},
        )

        return response.json()

    def list_result_samples(self, order_id: Union[str, UUID]) -> Dict:
        """
            Get all order's result samples.

            Args:
                order_id: Order id. Should be in uuid4 format.

            Returns:
                Dict: List of all order's result samples.
        """
        order_id = self.convert_str_to_uuid(order_id)

        response = self._make_api_call(requests.get, f'data/results/{str(order_id)}/samples')

        return response.json()
