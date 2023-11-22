""" Unit tests for user views
"""
from unittest.mock import patch, MagicMock

from django.test import SimpleTestCase, RequestFactory

from core_explore_federated_search_app.views.user.views import ViewData
from core_main_app.utils.tests_tools.MockUser import create_mock_user


class TestViewData(SimpleTestCase):
    """TestViewData"""

    def setUp(self):
        """setUp

        Returns:

        """
        self.factory = RequestFactory()
        self.user1 = create_mock_user(user_id="1")

    @patch(
        "core_explore_federated_search_app.components.data.api.get_data_from_instance"
    )
    @patch("core_main_app.utils.view_builders.data.render_page")
    def test_view_data_returns_rendered_page(
        self, mock_render_page, mock_get_data_from_instance
    ):
        """test_view_data_returns_rendered_page

        Returns:

        """
        # Arrange
        mock_get_data_from_instance.return_value = MagicMock(
            text='{"title":"test", "xml_content":"<root><value>test</value></root>", "template":{"_hash":"1234","format":"XSD", "_display_name":"test_1"}}'
        )
        request = self.factory.get(
            "core_explore_federated_search_app_data_detail"
        )
        request.user = self.user1
        request.GET = {
            "id": "1",
            "instance_name": "mdcs",
        }

        # Act
        ViewData.as_view()(request)

        # Assert
        self.assertTrue(mock_render_page.called)
