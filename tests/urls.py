""" Url router for the explore federated search application
"""
from django.conf.urls import include
from django.urls import re_path

import core_explore_federated_search_app.views.user.ajax as user_ajax
import core_explore_federated_search_app.views.user.views as user_views

urlpatterns = [
    re_path(r"^", include("core_main_app.urls")),
    re_path(
        r"^get_data_sources",
        user_ajax.get_data_source_list_federated,
        name="core_explore_federated_search_app_get_data_sources",
    ),
    re_path(
        r"^update_data_sources",
        user_ajax.update_data_source_list_federated,
        name="core_explore_federated_search_app_update_data_sources",
    ),
    re_path(
        r"^data",
        user_views.ViewData.as_view(),
        name="core_explore_federated_search_app_data_detail",
    ),
    re_path(r"^rest/", include("core_explore_federated_search_app.rest.urls")),
]
