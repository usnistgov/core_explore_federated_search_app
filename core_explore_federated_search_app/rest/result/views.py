""" REST views for the data API
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core_explore_common_app.utils.result.result import (
    get_result_from_rest_data_response,
)
from core_explore_federated_search_app.components.data.api import get_data_from_instance
from core_explore_federated_search_app.rest.result.serializers import (
    ResultDetailSerializer,
)


@schema(None)
class ResultDetail(APIView):
    """Result Detail API view"""

    def get(self, request):
        """Access data, Return Result, Expect a data ID and a Remote name in parameters

        Parameters:

            {
                "id" : "data_id",
                "instance_name" : "endpoint_name"
            }

        Args:

            request:

        Returns:

            - code: 200
              content: Data
            - code: 400
              content: Validation error
            - code: 500
              content: Internal server error
        """
        try:
            # Build serializer
            serializer = ResultDetailSerializer(data=request.query_params)
            # Validation
            serializer.is_valid(True)
            # reverse url for accessing data
            data_url = reverse(
                "core_main_app_rest_data_detail",
                kwargs={"pk": serializer.validated_data["id"]},
            )

            response = get_data_from_instance(
                serializer.validated_data["instance_name"], data_url, request.user
            )
            # if got a response from data
            if response.status_code == 200:
                # Serialize results
                return_value = get_result_from_rest_data_response(response)
                # Returns the response
                return Response(return_value, status=status.HTTP_200_OK)
            # if there no data we return the response given by the remote
            return Response(status=response.status_code)
        except ValidationError as validation_exception:
            content = {"message": validation_exception.detail}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exception:
            # if something went wrong, return an internal server error
            content = {"message": str(exception)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
