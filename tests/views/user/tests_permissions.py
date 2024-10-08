""" Permission tests on views
"""

from django.test import RequestFactory, override_settings
from tests.fixtures import AccessControlDataFixture

from core_explore_federated_search_app.views.user.ajax import (
    get_data_source_list_federated,
    update_data_source_list_federated,
)
from core_explore_federated_search_app.views.user.views import ViewData
from core_main_app.utils.integration_tests.integration_base_test_case import (
    IntegrationBaseTestCase,
)
from core_main_app.utils.tests_tools.MockUser import create_mock_user


class TestGetDataSourceListFederated(IntegrationBaseTestCase):
    """Test Get Data Source List Federated"""

    def setUp(self):
        """setUp"""

        self.factory = RequestFactory()
        self.user1 = create_mock_user(user_id="1")
        self.anonymous = create_mock_user(user_id=None, is_anonymous=True)
        self.fixture = AccessControlDataFixture()
        self.fixture.insert_data()

    def test_an_anonymous_user_can_not_access_data_sources_of_a_user_query(
        self,
    ):
        """test_an_anonymous_user_can_not_access_data_sources_of_a_user_query"""

        request = self.factory.get(
            "core_explore_federated_search_app_get_data_sources"
        )
        request.user = self.anonymous
        request.GET = {"id_query": str(self.fixture.query_user1.id)}
        response = get_data_source_list_federated(request)
        self.assertEqual(response.status_code, 403)


class TestUpdateDataSourceListFederated(IntegrationBaseTestCase):
    """Test Update Data Source List Federated"""

    def setUp(self):
        """setUp"""

        self.factory = RequestFactory()
        self.user1 = create_mock_user(user_id="1")
        self.anonymous = create_mock_user(user_id=None, is_anonymous=True)
        self.fixture = AccessControlDataFixture()
        self.fixture.insert_data()

    def test_an_anonymous_user_can_not_access_data_sources_of_a_user_query(
        self,
    ):
        """test_an_anonymous_user_can_not_access_data_sources_of_a_user_query"""

        request = self.factory.get(
            "core_explore_federated_search_app_update_data_sources"
        )
        request.user = self.anonymous
        request.GET = {"id_query": str(self.fixture.query_user1.id)}
        response = update_data_source_list_federated(request)
        self.assertEqual(response.status_code, 403)


class TestViewData(IntegrationBaseTestCase):
    """Test View Data"""

    def setUp(self):
        """setUp"""

        self.factory = RequestFactory()
        self.user1 = create_mock_user(user_id="1")
        self.anonymous = create_mock_user(user_id=None, is_anonymous=True)
        self.fixture = AccessControlDataFixture()
        self.fixture.insert_data()

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=False)
    def test_an_anonymous_user_can_not_access_a_data_that_is_not_in_a_workspace(
        self,
    ):
        """test_an_anonymous_user_can_not_access_a_data_that_is_not_in_a_workspace"""

        request = self.factory.get(
            "core_explore_federated_search_app_data_detail"
        )
        request.user = self.anonymous
        request.GET = {
            "instance_name": "Local",
            "id": str(self.fixture.data_no_workspace.id),
        }
        response = ViewData.as_view()(request)
        self.assertTrue(
            self.fixture.data_no_workspace.title
            not in response.content.decode()
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            "/accounts/login/?next=/core_explore_federated_search_app_data_detail",
        )

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=False)
    def test_an_anonymous_user_can_not_access_a_data_that_is_in_a_private_workspace(
        self,
    ):
        """test_an_anonymous_user_can_not_access_a_data_that_is_in_a_private_workspace"""

        request = self.factory.get(
            "core_explore_federated_search_app_data_detail"
        )
        request.user = self.anonymous
        request.GET = {
            "instance_name": "Local",
            "id": str(self.fixture.data_private_workspace.id),
        }
        response = ViewData.as_view()(request)
        self.assertTrue(
            self.fixture.data_private_workspace.title
            not in response.content.decode()
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            "/accounts/login/?next=/core_explore_federated_search_app_data_detail",
        )

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=False)
    def test_an_anonymous_user_can_not_access_a_data_that_is_in_a_public_workspace_and_access_setting_is_false(
        self,
    ):
        """test_an_anonymous_user_can_not_access_a_data_that_is_in_a_public_workspace_and_access_setting_is_false"""
        request = self.factory.get(
            "core_explore_federated_search_app_data_detail"
        )
        request.user = self.anonymous
        request.GET = {
            "instance_name": "Local",
            "id": str(self.fixture.data_public_workspace.id),
        }
        response = ViewData.as_view()(request)
        self.assertTrue(
            self.fixture.data_public_workspace.title
            not in response.content.decode()
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            "/accounts/login/?next=/core_explore_federated_search_app_data_detail",
        )
