""" Federated user views
"""
import json

from django.urls import reverse

from core_main_app.access_control.exceptions import AccessControlError
from core_main_app.commons import exceptions
from core_main_app.utils.view_builders import data as data_view_builder
from core_main_app.views.common.views import CommonView
from core_explore_federated_search_app.components.data.api import get_data_from_instance


class ViewData(CommonView):
    """View detail from remote data."""

    def get(self, request):
        # get parameters
        data_id = request.GET["id"]
        instance_name = request.GET["instance_name"]

        try:
            # FIXME unify with REST APIs
            data_url = "{0}?id={1}".format(
                reverse("core_main_app_rest_data_get_by_id_with_template_info"),
                str(data_id),
            )

            # execute request
            response = get_data_from_instance(instance_name, data_url, request.user)
            record = json.loads(response.text)

            # data to context
            data_object = {
                "fede_data_id": data_id,
                "title": record["title"],
                "xml_content": record["xml_content"],
                "template": {
                    "hash": record["template"]["hash"],
                    "display_name": record["template"]["_display_name"],
                },
            }

            page_context = data_view_builder.build_page(data_object)

            return data_view_builder.render_page(
                request,
                self.common_render,
                "core_main_app/user/data/detail.html",
                page_context,
            )
        except exceptions.DoesNotExist:
            error_message = (
                f"The instance with the name: {instance_name} does not exist"
            )
            status_code = 404
        except AccessControlError:
            error_message = "Access Forbidden"
            status_code = 403
        except Exception as exception:
            error_message = f"An error occurred: {str(exception)}"
            status_code = 400

        return self.common_render(
            request,
            "core_main_app/common/commons/error.html",
            context={"error": error_message, "status_code": status_code},
        )
