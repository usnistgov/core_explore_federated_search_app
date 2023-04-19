""" Access Control test for the data api
"""
from django.contrib.auth.models import AnonymousUser
from django.test import override_settings

from core_explore_federated_search_app.components.data.api import (
    get_data_from_instance,
)
from core_main_app.access_control.exceptions import AccessControlError
from core_main_app.utils.integration_tests.integration_base_test_case import (
    IntegrationBaseTestCase,
)
from tests.fixtures.fixtures import AccessControlDataFixture

fixture_data = AccessControlDataFixture()


class TestGetDataFromInstance(IntegrationBaseTestCase):
    """Test Get Data From Instance"""

    fixture = fixture_data

    @override_settings(CAN_ANONYMOUS_ACCESS_PUBLIC_DOCUMENT=False)
    def test_get_data_from_instance_raises_access_control_error_for_anonymous_user(
        self,
    ):
        """test_get_data_from_instance_raises_access_control_error_for_anonymous_user"""
        mock_user = AnonymousUser()
        with self.assertRaises(AccessControlError):
            get_data_from_instance("Instance Name", "Data URL", mock_user)
