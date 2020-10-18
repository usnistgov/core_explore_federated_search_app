""" Data api
"""
from urllib.parse import urljoin

import core_federated_search_app.components.instance.api as instance_api
from core_explore_common_app.utils.protocols.oauth2 import (
    send_get_request as oauth2_get_request,
)
from core_main_app.access_control import (
    api as main_access_control_api,
)
from core_main_app.access_control.decorators import access_control


@access_control(main_access_control_api.can_anonymous_access_public_data)
def get_data_from_instance(instance_name, data_url, user):
    """Retrieve a document from a given federated instance

    Args:
        instance_name:
        data_url:
        user:

    Returns:
    """
    instance = instance_api.get_by_name(instance_name)
    url_get_data = urljoin(instance.endpoint, data_url)

    return oauth2_get_request(url_get_data, instance.access_token)
