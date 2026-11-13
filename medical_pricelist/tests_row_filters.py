"""get_queryset honours the OP-2029 validity contract (epic OP-3317, phase 1).

Explicit validity values return the expected rows; a caller asking for
nothing gets what it got before the contract existed.
"""

from datetime import timedelta

from django.test import TestCase

from core.models.row_filters import Validity
from core.test_helpers import assert_row_filters, create_test_interactive_user, mark_deleted
from location.test_helpers import create_test_health_facility
from medical_pricelist.models import ItemsPricelist
from medical_pricelist.test_helpers import create_test_item_pricelist


class PricelistRowFiltersTest(TestCase):
    def test_items_pricelist(self):
        user = create_test_interactive_user(username="pricelistrowfilters")
        location_id = create_test_health_facility(code="RWF1").location_id
        live = create_test_item_pricelist(location_id)
        deleted = mark_deleted(create_test_item_pricelist(location_id))
        assert_row_filters(
            self, ItemsPricelist, ItemsPricelist.objects.filter(id__in=[live.id, deleted.id]), user,
            live.id, deleted.id, default_hides_deleted=False,
        )

    def test_a_validity_date_is_accepted(self):
        user = create_test_interactive_user(username="pricelistrowfilters")
        location_id = create_test_health_facility(code="RWF2").location_id
        pricelist = create_test_item_pricelist(location_id)
        rows = ItemsPricelist.objects.filter(id=pricelist.id)
        before = Validity.at(pricelist.validity_from - timedelta(days=1))
        self.assertFalse(ItemsPricelist.get_queryset(rows, user, validity=before).exists())
