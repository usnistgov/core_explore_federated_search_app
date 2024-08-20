""" Unit tests for `core_explore_federated_search_app.rest.query.views` package.
"""

from unittest import TestCase
from unittest.mock import patch, MagicMock

from rest_framework import status

from core_explore_federated_search_app.rest.query import views as query_views
from core_main_app.settings import MAX_DOCUMENT_LIST


class TestExecuteFederatedQueryViewBuildResponse(TestCase):
    """Unit tests for `ExecuteFederatedQueryView.build_response` method."""

    def setUp(self):
        """setUp"""
        self.mock_request = MagicMock()
        self.mock_request.data = {}

        self.mock_view = query_views.ExecuteFederatedQueryView()
        self.mock_view.request = self.mock_request

        self.mock_kwargs = {"data_list": MagicMock()}

    @patch.object(query_views, "json")
    def test_options_reloaded_from_string(self, mock_json):
        """test_options_reloaded_from_string"""
        self.mock_view.build_response(**self.mock_kwargs)

        mock_json.loads.assert_called_with("{}")

    @patch.object(query_views, "StandardResultsSetPagination")
    def test_standards_results_set_pagination_init(self, mock_paginator):
        """test_standards_results_set_pagination_init"""
        self.mock_view.build_response(**self.mock_kwargs)
        mock_paginator.assert_called()

    def test_all_data_list_too_large_triggers_400(self):
        """test_all_data_list_too_large_triggers_400"""
        self.mock_view.request.data["all"] = "true"
        self.mock_kwargs["data_list"].count.return_value = (
            MAX_DOCUMENT_LIST + 1
        )

        self.assertEqual(
            self.mock_view.build_response(**self.mock_kwargs).status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    @patch.object(query_views, "StandardResultsSetPagination")
    def test_not_all_queryset_is_paginated(self, mock_paginator):
        """test_not_all_queryset_is_paginated"""
        self.mock_view.build_response(**self.mock_kwargs)
        mock_paginator().paginate_queryset.assert_called_with(
            self.mock_kwargs["data_list"], self.mock_view.request
        )

    @patch.object(query_views, "StandardResultsSetPagination")
    @patch.object(query_views, "get_content_by_xpath")
    def test_data_xpath_is_retrieved_when_xpath_specified(
        self, mock_get_content_by_xpath, mock_paginator
    ):
        """test_data_xpath_is_retrieved_when_xpath_specified"""
        mock_paginated_data = MagicMock()
        mock_xml_content = MagicMock()

        mock_paginated_data.xml_content = mock_xml_content
        mock_paginator().paginate_queryset.return_value = [mock_paginated_data]

        mock_get_content_by_xpath.return_value = mock_xml_content

        mock_xpath = MagicMock()
        self.mock_view.request.data["xpath"] = mock_xpath
        mock_namespaces = MagicMock()
        self.mock_view.request.data["namespaces"] = mock_namespaces

        self.mock_view.build_response(**self.mock_kwargs)

        mock_get_content_by_xpath.assert_called_with(
            mock_xml_content, mock_xpath, namespaces=mock_namespaces
        )

    @patch.object(query_views, "StandardResultsSetPagination")
    @patch.object(query_views, "result_utils")
    def test_template_info_is_retrieved(
        self, mock_result_utils, mock_paginator
    ):
        """test_template_info_is_retrieved"""
        mock_paginated_data = MagicMock()
        mock_template = MagicMock()

        mock_paginated_data.template = mock_template
        mock_paginator().paginate_queryset.return_value = [mock_paginated_data]

        self.mock_view.build_response(**self.mock_kwargs)

        mock_result_utils.get_template_info.assert_called_with(
            mock_template, include_template_id=False
        )

    @patch.object(query_views, "StandardResultsSetPagination")
    @patch.object(query_views, "result_utils")
    @patch.object(query_views, "ResultSerializer")
    def test_paginated_response_is_called(
        self, mock_result_serializer, mock_result_utils, mock_paginator
    ):
        """test_paginated_response_is_called"""
        mock_paginated_data = MagicMock()
        mock_template = MagicMock()

        mock_paginated_data.template = mock_template
        mock_paginator().paginate_queryset.return_value = [mock_paginated_data]

        self.mock_view.build_response(**self.mock_kwargs)

        mock_paginator().get_paginated_response.assert_called_with(
            mock_result_serializer().data
        )

    @patch.object(query_views, "StandardResultsSetPagination")
    @patch.object(query_views, "result_utils")
    @patch.object(query_views, "ResultSerializer")
    def test_paginated_response_is_returned(
        self, mock_result_serializer, mock_result_utils, mock_paginator
    ):
        """test_paginated_response_is_returned"""
        mock_paginated_data = MagicMock()
        mock_template = MagicMock()

        mock_paginated_data.template = mock_template
        mock_paginator().paginate_queryset.return_value = [mock_paginated_data]

        expected_response = MagicMock()
        mock_paginator().get_paginated_response.return_value = (
            expected_response
        )

        self.assertEqual(
            self.mock_view.build_response(**self.mock_kwargs),
            expected_response,
        )

    @patch.object(query_views, "Response")
    @patch.object(query_views, "result_utils")
    @patch.object(query_views, "ResultSerializer")
    def test_paginated_response_is_returned_for_all_data(
        self, mock_result_serializer, mock_result_utils, mock_response
    ):
        """test_paginated_response_is_returned_for_all_data"""
        self.mock_view.request.data["all"] = "true"
        self.mock_kwargs["data_list"].count.return_value = (
            MAX_DOCUMENT_LIST - 1
        )

        expected_response = MagicMock()
        mock_response.return_value = expected_response

        self.assertEqual(
            self.mock_view.build_response(**self.mock_kwargs),
            expected_response,
        )


class TestExecuteFederatedQueryViewBuildTemplateIdList(TestCase):
    """Unit tests for `ExecuteFederatedQueryView.build_template_id_list` method."""

    def setUp(self):
        """setUp"""
        self.mock_request = MagicMock()
        self.mock_request.data = {}

        self.mock_view = query_views.ExecuteFederatedQueryView()
        self.mock_view.request = self.mock_request

        self.mock_template = MagicMock()
        self.mock_kwargs = {"template_list": [self.mock_template]}

    @patch.object(query_views, "parse_property")
    @patch.object(query_views, "template_api")
    def test_parse_property_called(
        self, mock_template_api, mock_parse_property
    ):
        """test_parse_property_called"""
        self.mock_view.build_template_id_list(**self.mock_kwargs)
        mock_parse_property.assert_called_with(self.mock_template, "hash")

    @patch.object(query_views, "parse_property")
    @patch.object(query_views, "template_api")
    def test_get_all_accessible_by_hash_called(
        self, mock_template_api, mock_parse_property
    ):
        """test_get_all_accessible_by_hash_called"""
        mock_template_hash = MagicMock()
        mock_parse_property.return_value = mock_template_hash

        self.mock_view.build_template_id_list(**self.mock_kwargs)
        mock_template_api.get_all_accessible_by_hash.assert_called_with(
            mock_template_hash, request=self.mock_view.request
        )

    @patch.object(query_views, "parse_property")
    @patch.object(query_views, "template_api")
    def test_return_template_id_list(
        self, mock_template_api, mock_parse_property
    ):
        """test_return_template_id_list"""
        mock_template_list = [MagicMock()]
        mock_template_api.get_all_accessible_by_hash.return_value = (
            mock_template_list
        )

        self.assertEqual(
            self.mock_view.build_template_id_list(**self.mock_kwargs),
            [template.id for template in mock_template_list],
        )
