from core.rights_role_test_case import RightsRoleGraphQLTestCase
from core.test_helpers import (
    create_medical_advisor_role,
    create_raf_role,
    create_right_only_user,
    create_role_user,
)
from location.test_helpers import create_basic_test_locations


ITEM_PL_QUERY = """
query {
  itemsPricelists(first: 5) {
    edges { node { id uuid name } }
  }
}
"""

SERVICE_PL_QUERY = """
query {
  servicesPricelists(first: 5) {
    edges { node { id uuid name } }
  }
}
"""


class MedicalPricelistRightsTests(RightsRoleGraphQLTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_basic_test_locations()

    def test_query_item_pricelists_right(self):
        allowed = create_right_only_user(
            "r_pli",
            ["gql_query_pricelists_medical_items_perms"],
            district_codes=self.DISTRICT_CODES,
        )
        denied = create_right_only_user("r_pli_no", [], district_codes=self.DISTRICT_CODES)
        self.assert_gql_ok(allowed, ITEM_PL_QUERY)
        self.assert_gql_unauthorized(denied, ITEM_PL_QUERY)

    def test_query_service_pricelists_right(self):
        allowed = create_right_only_user(
            "r_pls",
            ["gql_query_pricelists_medical_services_perms"],
            district_codes=self.DISTRICT_CODES,
        )
        denied = create_right_only_user("r_pls_no", [], district_codes=self.DISTRICT_CODES)
        self.assert_gql_ok(allowed, SERVICE_PL_QUERY)
        self.assert_gql_unauthorized(denied, SERVICE_PL_QUERY)


class MedicalPricelistRoleTests(RightsRoleGraphQLTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_basic_test_locations()
        cls.users = {
            "medical_advisor": create_role_user(
                "pl_ma", create_medical_advisor_role(), district_codes=cls.DISTRICT_CODES
            ),
            "raf": create_role_user(
                "pl_raf", create_raf_role(), district_codes=cls.DISTRICT_CODES
            ),
        }

    def test_roles_can_query_pricelists(self):
        for name, user in self.users.items():
            with self.subTest(role=name):
                self.assert_user_has_named_perms(
                    user, ["gql_query_pricelists_medical_items_perms"]
                )
                self.assert_user_has_named_perms(
                    user, ["gql_query_pricelists_medical_services_perms"]
                )
                self.assert_gql_ok(user, ITEM_PL_QUERY)
                self.assert_gql_ok(user, SERVICE_PL_QUERY)
