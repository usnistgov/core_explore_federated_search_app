""" Authentication tests for `core_explore_federated_search_app.rest.query.views`
package.
"""

from unittest import TestCase
from unittest.mock import patch

from django.test import override_settings
from rest_framework import status

from core_explore_federated_search_app.rest.query import views as query_views
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock


class TestExecuteFederatedQueryViewPermissions(TestCase):
    """Permissions tests for `ExecuteFederatedQueryView` view."""

    def setUp(self):
        """setUp"""
        self.mock_data = {"query": {}}

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=True)
    def test_anonymous_on_public_instance_returns_200(self):
        """test_anonymous_on_public_instance_returns_200"""
        response = RequestMock.do_request_post(
            query_views.ExecuteFederatedQueryView.as_view(),
            data=self.mock_data,
            user=None,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=False)
    def test_anonymous_on_private_instance_returns_403(self):
        """test_anonymous_on_private_instance_returns_403"""
        response = RequestMock.do_request_post(
            query_views.ExecuteFederatedQueryView.as_view(),
            data=self.mock_data,
            user=None,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=False)
    @patch.object(
        query_views.AbstractExecuteLocalQueryView, "execute_raw_query"
    )
    def test_registered_returns_200(self, mock_execute_raw_query):
        """test_registered_returns_200"""
        mock_execute_raw_query.return_value = []
        mock_user = create_mock_user(1)

        response = RequestMock.do_request_post(
            query_views.ExecuteFederatedQueryView.as_view(),
            data=self.mock_data,
            user=mock_user,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=False)
    @patch.object(
        query_views.AbstractExecuteLocalQueryView, "execute_raw_query"
    )
    def test_staff_returns_200(self, mock_execute_raw_query):
        """test_staff_returns_200"""
        mock_execute_raw_query.return_value = []
        mock_user = create_mock_user(1, is_staff=True, is_superuser=False)

        response = RequestMock.do_request_post(
            query_views.ExecuteFederatedQueryView.as_view(),
            data=self.mock_data,
            user=mock_user,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
