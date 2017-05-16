""" REST views for the data API
"""
from urlparse import urljoin

from django.core.urlresolvers import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from core_explore_common_app.utils.protocols.commons import get_url
from core_explore_common_app.utils.protocols.oauth2 import send_get_request as oauth2_request
from rest_framework import status
from core_explore_common_app.utils.result.result import get_result_from_rest_data_response
import core_explore_federated_search_app.components.instance.api as instance_api


@api_view(['GET'])
def get_result_from_data_id(request):
    """ Access data, Returns Result, Expects an data ID and an Remote name in parameters

    Args:
        request:

    Returns:

    """
    try:
        # get parameters
        data_id = request.GET.get('id', None)
        instance_name = request.GET.get('instance_name', None)

        # if no data id given
        if data_id is None:
            content = {'message': "data id is missing"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # if no instance name given
        if instance_name is None:
            content = {'message': "instance name is missing"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # reverse url for accessing data
        url_get_data = reverse("core_main_app_rest_data_get_by_id")

        # requests the remote instance
        instance = instance_api.get_by_name(instance_name)
        url_base = get_url(instance.protocol, instance.address, instance.port)
        response = oauth2_request("{0}?id={1}".format(urljoin(url_base, url_get_data), data_id), instance.access_token)

        # if got a response from data
        if response.status_code == 200:
            # Serialize results
            return_value = get_result_from_rest_data_response(response)
            # Returns the response
            return Response(return_value, status=status.HTTP_200_OK)
        # if there no data we return the response given by the remote
        else:
            return response
    except Exception as e:
        # if something went wrong, return an internal server error
        content = {'message': e.message}
        return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
