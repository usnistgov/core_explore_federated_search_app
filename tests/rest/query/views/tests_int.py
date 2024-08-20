""" Integration tests for `core_federated_search.rest.query.views` package.
"""

from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework import status

from core_explore_federated_search_app.rest.query import views as query_views
from core_main_app.utils.integration_tests.integration_base_transaction_test_case import (
    IntegrationTransactionTestCase,
)
from core_main_app.utils.tests_tools.MockUser import create_mock_user
from core_main_app.utils.tests_tools.RequestMock import RequestMock
from tests.fixtures import AccessControlDataFixture


class TestExecuteFederatedQueryView(IntegrationTransactionTestCase):
    """Integration tests for `ExecuteFederatedQueryView` view."""

    fixture = AccessControlDataFixture()

    def setUp(self):
        """setUp"""
        super().setUp()
        self.mock_logged_user = None

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=True)
    def test_anonymous_retrieve_only_public_data_on_public_repo(self):
        """test_anonymous_retrieve_only_public_data_on_public_repo"""
        mock_user = create_mock_user("0", is_anonymous=True)

        response = RequestMock.do_request_post(
            query_views.ExecuteFederatedQueryView.as_view(),
            mock_user,
            data={"query": {}},
        )

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Data public")

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=False)
    def test_anonymous_cannot_retrieve_data_on_private_repo(self):
        """test_anonymous_cannot_retrieve_data_on_private_repo"""
        mock_user = create_mock_user("0", is_anonymous=True)

        response = RequestMock.do_request_post(
            query_views.ExecuteFederatedQueryView.as_view(),
            mock_user,
            data={"query": {}},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=True)
    def test_logged_user_can_retrieve_public_and_owned_data_on_public_repo(
        self,
    ):
        """test_logged_user_can_retrieve_public_and_owned_data_on_public_repo"""
        mock_user = User.objects.create_user(
            "mock_user", password="mock_password"
        )

        response = RequestMock.do_request_post(
            query_views.ExecuteFederatedQueryView.as_view(),
            mock_user,
            data={"query": {}},
        )

        self.assertEqual(len(response.data["results"]), 2)

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=False)
    def test_logged_user_can_retrieve_public_and_owned_data_on_private_repo(
        self,
    ):
        """test_logged_user_can_retrieve_public_and_owned_data_on_private_repo"""
        mock_user = User.objects.create_user(
            "mock_user", password="mock_password"
        )

        response = RequestMock.do_request_post(
            query_views.ExecuteFederatedQueryView.as_view(),
            mock_user,
            data={"query": {}},
        )

        self.assertEqual(len(response.data["results"]), 2)

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=True)
    def test_duplicate_returns_correct_data_len(self):
        """test_duplicate_returns_correct_data_len"""
        mock_user = User.objects.create_user(
            "mock_user", password="mock_password"
        )

        template_hash = self.fixture.template.hash

        response = RequestMock.do_request_post(
            query_views.ExecuteFederatedQueryView.as_view(),
            mock_user,
            data={
                "query": {},
                "templates": [
                    {"id": 1, "hash": template_hash},
                    {"id": 5, "hash": template_hash},
                    {"id": 7, "hash": f"{template_hash}anotherhash"},
                ],
            },
        )

        self.assertEqual(len(response.data["results"]), 2)

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=True)
    def test_duplicate_hash_does_not_return_duplicate_data(self):
        """test_duplicate_hash_does_not_return_duplicate_data"""
        mock_user = User.objects.create_user(
            "mock_user", password="mock_password"
        )

        template_hash = self.fixture.template.hash

        response = RequestMock.do_request_post(
            query_views.ExecuteFederatedQueryView.as_view(),
            mock_user,
            data={
                "query": {},
                "templates": [
                    {"id": 1, "hash": template_hash},
                    {"id": 5, "hash": template_hash},
                    {"id": 7, "hash": f"{template_hash}anotherhash"},
                ],
            },
        )

        self.assertNotEqual(
            response.data["results"][0], response.data["results"][1]
        )
