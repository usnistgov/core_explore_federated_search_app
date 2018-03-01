""" REST views for the query API
"""
from django.core.urlresolvers import reverse
from core_explore_common_app.components.result.models import Result
from core_explore_common_app.rest.result.serializers import ResultSerializer
from core_explore_common_app.utils.pagination.rest_framework_paginator.pagination import StandardResultsSetPagination
from core_main_app.components.template.api import get_all_by_hash
from core_explore_common_app.utils.query.mongo.query_builder import QueryBuilder
from rest_framework.decorators import api_view, schema
from rest_framework.response import Response
from rest_framework import status
from core_explore_common_app.utils.result import result as result_utils
import core_main_app.components.data.api as data_api
import json


@api_view(['POST'])
@schema(None)
def execute_query(request):
    """ Execute query and return result.

    Args:
        request:

    Returns:

    """
    try:
        # get query
        query = request.POST.get('query', None)
        options = request.POST.get('options', None)

        if query is not None:
            query_builder = QueryBuilder(query, 'dict_content')
        else:
            return Response('Query should be passed in parameters', status=status.HTTP_400_BAD_REQUEST)

        # update the content query with given templates
        if 'templates' in request.POST:
            templates = json.loads(request.POST['templates'])
            _update_query_builder(query_builder, templates)

        # create a raw query
        raw_query = query_builder.get_raw_query()

        # execute query
        data_list = data_api.execute_query(raw_query, request.user)

        # get paginator
        paginator = StandardResultsSetPagination()

        # get request page from list of results
        page = paginator.paginate_queryset(data_list, request)

        # Serialize object
        results = []
        url = reverse("core_explore_federated_search_app_data_detail")
        url_access_data = reverse("core_explore_federated_search_app_rest_get_result_from_data_id")

        instance_name = ''
        json_options = json.loads(options)
        if options is not None:
            instance_name = json_options['instance_name']

        # Template info
        template_info = dict()
        for data in page:
            # get data's template
            template = data.template
            # get and store data's template information
            if template not in template_info:
                template_info[template] = result_utils.get_template_info(template, include_template_id=False)

            results.append(Result(title=data.title,
                                  xml_content=data.xml_content,
                                  template_info=template_info[template],
                                  detail_url="{0}?id={1}&instance_name={2}".format(url, data.id, instance_name),
                                  access_data_url="{0}?id={1}&instance_name={2}".format(url_access_data,
                                                                                        data.id, instance_name)))

        return_value = ResultSerializer(results, many=True)

        return paginator.get_paginated_response(return_value.data)
    except Exception as api_exception:
        content = {'message': api_exception.message}
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _update_query_builder(query_builder, templates):
    """ Update the query criteria with a list of templates.

    Args:
        query_builder:
        templates:

    Returns:

    """
    if len(templates) > 0:
        template_id_list = []
        for template in templates:
            template_id_list.extend(get_all_by_hash(template['hash']).values_list('id'))

        # Even if the list is empty, we add it to the query
        # empty list means there is no equal template with the hash given
        query_builder.add_list_templates_criteria(template_id_list)
