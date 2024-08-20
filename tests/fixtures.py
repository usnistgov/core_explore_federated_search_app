""" Fixtures files for Data
"""

from core_explore_common_app.components.query.models import Query
from core_main_app.components.data.models import Data
from core_main_app.components.template.models import Template
from core_main_app.components.workspace.models import Workspace
from core_main_app.utils.integration_tests.fixture_interface import (
    FixtureInterface,
)


class AccessControlDataFixture(FixtureInterface):
    """Access Control Data fixture"""

    template = None
    workspace_user1 = None
    public_workspace = None
    data_collection = None
    data_no_workspace = None
    data_private_workspace = None
    data_public_workspace = None
    query_user1 = None

    def insert_data(self):
        """Insert a set of Data.

        Returns:

        """
        # Make a connexion with a mock database
        self.generate_template()
        self.generate_workspaces()
        self.generate_data_collection()
        self.generate_queries()

    def generate_data_collection(self):
        """Generate a Data collection.

        Returns:

        """

        content = {"root": {"element": "value2"}}

        common_data_items = {
            "template": self.template,
        }

        data_kwargs_no_workspace = {
            "title": "Data private no workspace",
            "user_id": "3",
        }
        self.data_no_workspace = Data(
            **common_data_items, **data_kwargs_no_workspace
        )
        self.data_no_workspace.save_object()

        data_kwargs_private_workspace = {
            "title": "Data private with workspace",
            "user_id": "1",
            "workspace": self.workspace_user1,
            "dict_content": content,
        }
        self.data_private_workspace = Data(
            **common_data_items, **data_kwargs_private_workspace
        )
        self.data_private_workspace.save_object()

        data_kwargs_public_workspace = {
            "title": "Data public",
            "user_id": "2",
            "workspace": self.public_workspace,
        }
        self.data_public_workspace = Data(
            **common_data_items, **data_kwargs_public_workspace
        )
        self.data_public_workspace.save_object()

        self.data_collection = [
            self.data_no_workspace,
            self.data_private_workspace,
            self.data_public_workspace,
        ]

    def generate_template(self):
        """Generate an unique Template.

        Returns:

        """
        self.template = Template()
        xsd = (
            '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">'
            '<xs:element name="tag"></xs:element></xs:schema>'
        )
        self.template.content = xsd
        self.template.hash = "mock_hash"
        self.template.filename = "filename.xsd"
        self.template.save()

    def generate_workspaces(self):
        """Generate the workspaces.

        Returns:

        """
        self.workspace_user1 = Workspace(
            title="Workspace 1", owner="1", read_perm_id="1", write_perm_id="1"
        )
        self.workspace_user1.save()
        self.public_workspace = Workspace(
            title="public",
            owner="1",
            read_perm_id="3",
            write_perm_id="3",
            is_public=True,
        )
        self.public_workspace.save()

    def generate_queries(self):
        """Generate queries

        Returns:

        """
        self.query_user1 = Query(user_id="1")
        self.query_user1.save()
