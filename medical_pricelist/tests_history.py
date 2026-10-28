import json

from django.conf import settings

from core.models.openimis_graphql_test_case import openIMISGraphQLTestCase, BaseTestContext
from core.test_helpers import create_test_interactive_user
from medical.test_helpers import create_test_item, create_test_service
from medical_pricelist.gql_mutations import create_or_update_pricelist
from medical_pricelist.models import (
    ItemsPricelist,
    ItemsPricelistDetail,
    ServicesPricelist,
    ServicesPricelistDetail,
)
from medical.models import Item, Service


class PricelistUpdateHistoryTest(openIMISGraphQLTestCase):
    """Updating a price list header must keep the previous version.

    The update path overwrote the live row in place, so the previous name/date
    was lost. A versioned update copies the old values into a historical row
    (legacy_id = live id, validity_to set) and keeps the live row (and its
    details) under the same id.
    """

    GRAPHQL_URL = f'/{settings.SITE_ROOT()}graphql'
    GRAPHQL_SCHEMA = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AUTH_HEADER = settings.GRAPHQL_JWT.get('JWT_AUTH_HEADER_PREFIX', 'Bearer')
        cls.admin_user = create_test_interactive_user(username="testPricelistHistAdmin")
        cls.admin_token = BaseTestContext(user=cls.admin_user).get_jwt()

    def _assert_update_keeps_history(
        self, prefix, pricelist_model, detail_model, element_model, element, query_name
    ):
        old_name = f"{prefix}-OLD"
        new_name = f"{prefix}-NEW"
        pricelist = create_or_update_pricelist(
            {
                "name": old_name,
                "pricelist_date": "2019-01-01",
                "audit_user_id": None,
                "added_details": [element.uuid],
            },
            self.admin_user,
            pricelist_model,
            element_model,
            detail_model,
        )
        live_id = pricelist.id

        create_or_update_pricelist(
            {
                "uuid": pricelist.uuid,
                "name": new_name,
                "pricelist_date": "2019-01-01",
                "audit_user_id": None,
            },
            self.admin_user,
            pricelist_model,
            element_model,
            detail_model,
        )

        history = pricelist_model.objects.filter(legacy_id=live_id)
        self.assertEqual(history.count(), 1, "the update must create exactly one historical row")
        histo = history.get()
        self.assertEqual(histo.name, old_name, "the historical row must keep the previous name")
        self.assertIsNotNone(histo.validity_to, "the historical row must be closed")
        self.assertNotEqual(histo.uuid, pricelist.uuid)

        live = pricelist_model.objects.get(id=live_id)
        self.assertEqual(live.name, new_name)
        self.assertIsNone(live.validity_to)
        self.assertIsNone(live.legacy_id)
        self.assertEqual(live.uuid, pricelist.uuid)

        live_details = detail_model.objects.filter(validity_to__isnull=True, **{
            f"{detail_model.model_prefix}__uuid": element.uuid,
        })
        self.assertEqual(live_details.count(), 1)
        self.assertEqual(
            getattr(live_details.get(), f"{detail_model.pricelist_field}_id"), live_id,
            "details must still belong to the live price list",
        )

        response = self.query(
            '''
            query {
                %s(showHistory: true, name_Istartswith: "%s") {
                    edges { node { name validityTo legacyId } }
                }
            }
            ''' % (query_name, prefix),
            headers={"HTTP_AUTHORIZATION": f"{self.AUTH_HEADER} {self.admin_token}"},
        )
        self.assertResponseNoErrors(response)
        nodes = [e["node"] for e in json.loads(response.content)["data"][query_name]["edges"]]
        self.assertEqual(sorted(n["name"] for n in nodes), sorted([new_name, old_name]))
        current = [n for n in nodes if n["validityTo"] is None]
        self.assertEqual([n["name"] for n in current], [new_name])

    def test_services_pricelist_update_keeps_history(self):
        service = create_test_service("A", custom_props={"code": "PLHS1"})
        self._assert_update_keeps_history(
            "PLHIST-SVC", ServicesPricelist, ServicesPricelistDetail, Service, service,
            "servicesPricelists",
        )

    def test_items_pricelist_update_keeps_history(self):
        item = create_test_item("D", custom_props={"code": "PLHI1"})
        self._assert_update_keeps_history(
            "PLHIST-ITM", ItemsPricelist, ItemsPricelistDetail, Item, item,
            "itemsPricelists",
        )
