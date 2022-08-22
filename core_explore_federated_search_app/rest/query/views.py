""" REST views for the query API
"""
import logging

import pytz
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import schema
from rest_framework.response import Response
from rest_framework.views import APIView

from core_main_app.components.template import api as template_api
from core_main_app.utils.pagination.rest_framework_paginator.pagination import (
    StandardResultsSetPagination,
)
from core_main_app.utils.query.mongo.query_builder import QueryBuilder
import core_main_app.components.data.api as data_api
from core_explore_common_app.components.result.models import Result
from core_explore_common_app.rest.result.serializers import ResultSerializer
from core_explore_common_app.utils.result import result as result_utils
from core_explore_federated_search_app import settings
from core_explore_federated_search_app.rest.query.serializers import (
    QueryExecuteSerializer,
)

logger = logging.getLogger(__name__)


@schema(None)
class QueryExecute(APIView):
    """Execute query endpoint"""

    def post(self, request):
        """Execute query

        Parameters:

            {
                "query" : "value",
                "options" : "number",
                "templates" : "[]"
            }

        Args:

            request: HTTP request

        Returns:

            - code: 200
              content: Paginated list of Data
            - code: 500
              content: Internal server error
        """
        try:
            # serialization
            serializer = QueryExecuteSerializer(data=request.data)
            # validation
            serializer.is_valid(True)

            # get the options
            options = None
            if "options" in serializer.validated_data:
                options = serializer.validated_data["options"]

            # get the query order by field
            order_by_field = (
                request.data["order_by_field"].split(",")
                if "order_by_field" in request.data
                else ""
            )

            # init a QueryBuilder with the query
            query_builder = QueryBuilder(
                serializer.validated_data["query"], "dict_content"
            )

            # update the content query with given templates
            if "templates" in serializer.validated_data:
                _update_query_builder(
                    query_builder,
                    serializer.validated_data["templates"],
                    request=request,
                )

            # create a raw query
            raw_query = query_builder.get_raw_query()
            # execute query
            data_list = data_api.execute_json_query(
                raw_query, request.user, order_by_field
            )
            # get paginator
            paginator = StandardResultsSetPagination()
            # get request page from list of results
            page = paginator.paginate_queryset(data_list, request)

            # Serialize object
            results = []
            url = reverse("core_explore_federated_search_app_data_detail")
            url_access_data = reverse(
                "core_explore_federated_search_app_rest_get_result_from_data_id"
            )

            instance_name = ""
            if options is not None:
                if "instance_name" in options:
                    instance_name = options["instance_name"]

            # Template info
            template_info = dict()

            # Change timezone depending on the request arguments. Default to settings
            # and ultimately to UTC if the setting is not present.
            try:
                user_timezone = pytz.timezone(
                    request.META.get("HTTP_TZ", getattr(settings, "TIME_ZONE", "UTC"))
                )
            except Exception as exc:
                logger.error(
                    f"Impossible to determine timezone from headers: {str(exc)}. Using "
                    f"settings timezone info."
                )
                user_timezone = pytz.timezone(getattr(settings, "TIME_ZONE", "UTC"))

            timezone.activate(user_timezone)

            for data in page:
                # get data's template
                template = data.template
                # get and store data's template information
                if template not in template_info:
                    template_info[template] = result_utils.get_template_info(
                        template, include_template_id=False
                    )

                results.append(
                    Result(
                        title=data.title,
                        xml_content=data.xml_content,
                        template_info=template_info[template],
                        permission_url=None,
                        detail_url="{0}?id={1}&instance_name={2}".format(
                            url, data.id, instance_name
                        ),
                        last_modification_date=data.last_modification_date.replace(
                            tzinfo=pytz.UTC
                        ),
                        access_data_url="{0}?id={1}&instance_name={2}".format(
                            url_access_data, data.id, instance_name
                        ),
                    )
                )

            return_value = ResultSerializer(results, many=True)

            return paginator.get_paginated_response(return_value.data)
        except Exception as api_exception:
            content = {"message": str(api_exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _update_query_builder(query_builder, templates, request=None):
    """Update the query criteria with a list of templates.

    Args:
        query_builder:
        templates:

    Returns:

    """
    if len(templates) > 0:
        template_id_list = []
        for template in templates:
            template_id_list.extend(
                template_api.get_all_accessible_by_hash(
                    template["hash"], request=request
                ).values_list("id", flat=True)
            )

        # Even if the list is empty, we add it to the query
        # empty list means there is no equal template with the hash given
        query_builder.add_list_criteria("template", template_id_list)
