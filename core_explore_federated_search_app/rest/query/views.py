""" REST views for the query API
"""

import json
import logging

import pytz
from django.urls import reverse
from rest_framework.decorators import schema
from rest_framework import status
from rest_framework.response import Response

from core_explore_common_app.components.result.models import Result
from core_explore_common_app.rest.result.serializers import ResultSerializer
from core_explore_common_app.utils.result import result as result_utils
from core_main_app.rest.data.serializers import DataWithTemplateInfoSerializer
from core_main_app.rest.data.abstract_views import (
    AbstractExecuteLocalQueryView,
)
from core_main_app.settings import MAX_DOCUMENT_LIST
from core_main_app.utils.boolean import to_bool
from core_main_app.utils.object import parse_property
from core_main_app.utils.pagination.rest_framework_paginator.pagination import (
    StandardResultsSetPagination,
)
from core_main_app.components.template import api as template_api
from core_main_app.utils.xml import get_content_by_xpath

logger = logging.getLogger(__name__)


@schema(None)
class ExecuteFederatedQueryView(AbstractExecuteLocalQueryView):
    """View called when executing a federated query."""

    serializer = DataWithTemplateInfoSerializer

    def build_response(self, data_list):
        """Build the response.

        Args:
            data_list: List of data

        Returns:
            The response paginated
        """
        xpath = self.request.data.get("xpath", None)
        namespaces = self.request.data.get("namespaces", None)
        options = json.loads(self.request.data.get("options", "{}"))

        if "all" in self.request.data and to_bool(self.request.data["all"]):
            if data_list.count() > MAX_DOCUMENT_LIST:
                content = {"message": "Number of documents is over the limit."}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            page = data_list
            response_fn = Response
        else:
            # Get paginator and requested page from list of results
            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(data_list, self.request)
            response_fn = paginator.get_paginated_response

        # Select values at xpath if provided
        if xpath:
            for data_object in page:
                data_object.xml_content = get_content_by_xpath(
                    data_object.xml_content, xpath, namespaces=namespaces
                )

        results = []
        template_info = {}

        instance_name = options.get("instance_name", "")
        detail_base_url = reverse(
            "core_explore_federated_search_app_data_detail"
        )
        access_data_base_url = reverse(
            "core_explore_federated_search_app_rest_get_result_from_data_id"
        )

        for data in page:
            template = data.template

            if template not in template_info:
                template_info[template] = result_utils.get_template_info(
                    template, include_template_id=False
                )

            data_query_string = f"id={data.id}&instance_name={instance_name}"
            results.append(
                Result(
                    title=data.title,
                    content=data.content,
                    template_info=template_info[template],
                    permission_url=None,
                    detail_url=f"{detail_base_url}?{data_query_string}",
                    last_modification_date=data.last_modification_date.replace(
                        tzinfo=pytz.UTC
                    ),
                    access_data_url=f"{access_data_base_url}?{data_query_string}",
                )
            )

        return response_fn(ResultSerializer(results, many=True).data)

    def build_template_id_list(self, template_list):
        """Retrieve list of template ID from a given list of template hash.

        Args:
            template_list: list - List of template hash.

        Returns:
            list - List of template IDs matching the input template hashes.
        """
        template_id_list = []

        for template in template_list:
            template_hash = parse_property(template, "hash")

            template_id_list += [
                template_by_hash.id
                for template_by_hash in template_api.get_all_accessible_by_hash(
                    template_hash, request=self.request
                )
            ]

        return template_id_list
