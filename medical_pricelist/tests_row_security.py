"""Row security on pricelist lines and pricelist mutations (OP-3322).

A pricelist is visible when its location sits in the user's districts, or when
it has no location; a price line is exactly as visible as its pricelist. Every
mutation target and every location written goes through that same scope.
"""

import json

from core.models.openimis_graphql_test_case import (
    BaseTestContext,
    openIMISGraphQLTestCase,
)
from core.test_helpers import create_hf_bound_role_user, create_right_only_user
from django.conf import settings
from location.models import Location
from location.test_helpers import create_basic_test_locations, create_test_health_facility
from medical.test_helpers import create_test_item, create_test_service

from medical_pricelist.gql_mutations import (
    CreateServicesPricelistMutation,
    DeleteItemsPricelistMutation,
    DeleteServicesPricelistMutation,
    UpdateServicesPricelistMutation,
)
from medical_pricelist.models import (
    ItemsPricelistDetail,
    ServicesPricelist,
    ServicesPricelistDetail,
)
from medical_pricelist.test_helpers import (
    create_test_item_pricelist,
    create_test_service_pricelist,
)

PRICELIST_PERMS = [
    "gql_query_pricelists_perms",
    "gql_query_pricelists_medical_services_perms",
    "gql_query_pricelists_medical_items_perms",
    "gql_mutation_pricelists_medical_services_add_perms",
    "gql_mutation_pricelists_medical_services_update_perms",
    "gql_mutation_pricelists_medical_services_delete_perms",
    "gql_mutation_pricelists_medical_items_delete_perms",
]

PRICES_QUERY = """
query ($s: Int, $i: Int) {
  pricelists(servicesPricelistId: $s, itemsPricelistId: $i) {
    services { id p }
    items { id p }
  }
}
"""


class PricelistRowSecurityTest(openIMISGraphQLTestCase):
    GRAPHQL_URL = f"/{settings.SITE_ROOT()}graphql"
    GRAPHQL_SCHEMA = True

    @classmethod
    def setUpTestData(cls):
        create_basic_test_locations()
        cls.own_district = Location.objects.get(code="R2D1", validity_to__isnull=True)
        cls.other_district = Location.objects.get(code="R1D1", validity_to__isnull=True)
        cls.user = create_right_only_user(
            "plRowSecUser", PRICELIST_PERMS, district_codes=["R2D1"]
        )
        cls.service = create_test_service("A", custom_props={"code": "PLRS-S"})
        cls.item = create_test_item("A", custom_props={"code": "PLRS-I"})

        cls.own_services = create_test_service_pricelist(
            cls.own_district.id, custom_props={"name": "own services"}
        )
        cls.other_services = create_test_service_pricelist(
            cls.other_district.id, custom_props={"name": "other services"}
        )
        cls.other_items = create_test_item_pricelist(
            cls.other_district.id, custom_props={"name": "other items"}
        )
        for pricelist in (cls.own_services, cls.other_services):
            ServicesPricelistDetail.objects.create(
                services_pricelist=pricelist,
                service=cls.service,
                price_overrule=7,
                validity_from="2019-01-01",
                audit_user_id=-1,
            )
        cls.other_item_line = ItemsPricelistDetail.objects.create(
            items_pricelist=cls.other_items,
            item=cls.item,
            price_overrule=3,
            validity_from="2019-01-01",
            audit_user_id=-1,
        )

    def _prices(self, user, services=None, items=None):
        response = self.query(
            PRICES_QUERY,
            headers={
                "HTTP_AUTHORIZATION": f"Bearer {BaseTestContext(user=user).get_jwt()}"
            },
            variables={"s": services, "i": items},
        )
        self.assertResponseNoErrors(response)
        return json.loads(response.content)["data"]["pricelists"]

    # -- model scope ------------------------------------------------------------

    def test_price_lines_follow_their_pricelist(self):
        visible = ServicesPricelistDetail.get_queryset(
            ServicesPricelistDetail.objects.all(), self.user
        )
        self.assertTrue(visible.filter(services_pricelist=self.own_services).exists())
        self.assertFalse(visible.filter(services_pricelist=self.other_services).exists())
        self.assertFalse(
            ItemsPricelistDetail.get_queryset(ItemsPricelistDetail.objects.all(), self.user)
            .filter(id=self.other_item_line.id)
            .exists()
        )

    # -- pricelists(...) --------------------------------------------------------

    def test_prices_of_a_pricelist_outside_scope_are_not_served(self):
        data = self._prices(self.user, services=self.other_services.id, items=self.other_items.id)
        self.assertEqual([], data["services"])
        self.assertEqual([], data["items"])

    def test_prices_of_a_pricelist_inside_scope_are_served(self):
        data = self._prices(self.user, services=self.own_services.id)
        self.assertEqual([self.service.id], [line["id"] for line in data["services"]])

    def test_own_health_facility_pricelist_is_served_whatever_its_location(self):
        # A facility in R2D1 whose pricelist sits in another district: its staff
        # still need its prices to enter claims.
        hf = create_test_health_facility(
            "PLRSHF", self.own_district.id, custom_props={"services_pricelist": self.other_services}
        )
        hf_user = create_hf_bound_role_user("plRowSecHf", None, health_facility=hf)
        data = self._prices(hf_user, services=self.other_services.id)
        self.assertEqual([self.service.id], [line["id"] for line in data["services"]])

    # -- mutations --------------------------------------------------------------

    def test_update_of_a_pricelist_outside_scope_is_refused(self):
        errors = UpdateServicesPricelistMutation.async_mutate(
            self.user,
            uuid=self.other_services.uuid,
            name="hijacked",
            pricelist_date="2020-01-01",
        )
        self.assertTrue(errors)
        self.other_services.refresh_from_db()
        self.assertEqual("other services", self.other_services.name)

    def test_create_at_a_location_outside_scope_is_refused(self):
        errors = CreateServicesPricelistMutation.async_mutate(
            self.user,
            name="created elsewhere",
            pricelist_date="2020-01-01",
            location_id=self.other_district.uuid,
        )
        self.assertTrue(errors)
        self.assertFalse(ServicesPricelist.objects.filter(name="created elsewhere").exists())

    def test_create_in_own_district_is_accepted(self):
        errors = CreateServicesPricelistMutation.async_mutate(
            self.user,
            name="created at home",
            pricelist_date="2020-01-01",
            location_id=self.own_district.uuid,
        )
        self.assertFalse(errors)
        self.assertTrue(ServicesPricelist.objects.filter(name="created at home").exists())

    def test_delete_of_a_pricelist_outside_scope_is_refused(self):
        for mutation, pricelist in (
            (DeleteServicesPricelistMutation, self.other_services),
            (DeleteItemsPricelistMutation, self.other_items),
        ):
            with self.subTest(mutation=mutation.__name__):
                errors = mutation.async_mutate(self.user, uuids=[pricelist.uuid])
                self.assertTrue(errors)
                pricelist.refresh_from_db()
                self.assertIsNone(pricelist.validity_to)

    def test_delete_mutations_log_their_own_class(self):
        self.assertEqual(
            "DeleteServicesPricelistMutation", DeleteServicesPricelistMutation._mutation_class
        )
        self.assertEqual(
            "DeleteItemsPricelistMutation", DeleteItemsPricelistMutation._mutation_class
        )
