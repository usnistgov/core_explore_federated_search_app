""" Federated user views
"""
import json
from urllib.parse import urljoin

from django.urls import reverse

import core_federated_search_app.components.instance.api as instance_api
from core_explore_common_app.utils.protocols.oauth2 import send_get_request
from core_main_app.commons import exceptions
from core_main_app.settings import INSTALLED_APPS
from core_main_app.views.common.views import CommonView


class ViewData(CommonView):
    """ View detail from remote data.
    """
    template = 'core_explore_federated_search_app/user/data_detail.html'

    def get(self, request):
        # get parameters
        data_id = request.GET['id']
        instance_name = request.GET['instance_name']

        try:
            # get instance information
            instance = instance_api.get_by_name(instance_name)

            # FIXME: reverse args
            # Get detail view base url (to be completed with data id)
            url = urljoin(instance.endpoint, reverse("core_main_app_rest_data_get_by_id_with_template_info"))
            url = "{0}?id={1}".format(url, str(data_id))

            # execute request
            response = send_get_request(url, instance.access_token)
            record = json.loads(response.text)

            # data to context
            data = {'title': record['title'],
                    'xml_content': record['xml_content'],
                    'template': {'hash': record['template']['hash'], 'display_name': record['template']['_display_name']}}

            context = {
                'data': data
            }

            assets = {
                "js": [
                    {
                        "path": 'core_main_app/common/js/XMLTree.js',
                        "is_raw": False
                    },
                    {
                        "path": 'core_main_app/user/js/data/detail.js',
                        "is_raw": False
                    },
                ],
                "css": ["core_main_app/common/css/XMLTree.css"],
            }

            modals = []

            if "core_file_preview_app" in INSTALLED_APPS:
                assets["js"].extend([
                    {
                        "path": 'core_file_preview_app/user/js/file_preview.js',
                        "is_raw": False
                    }
                ])
                assets["css"].append("core_file_preview_app/user/css/file_preview.css")
                modals.append("core_file_preview_app/user/file_preview_modal.html")

            return self.common_render(request,
                                      self.template,
                                      context=context,
                                      assets=assets,
                                      modals=modals)

        except exceptions.DoesNotExist as e:
            error_message = "The instance with the name: {0} does not exist".format(instance_name)
        except Exception as e:
            error_message = "An error occured: {0}".format(str(e))

        return self.common_render(request,
                                  'core_main_app/common/commons/error.html',
                                  context={"error": error_message})
