from location.models import HealthFacility
from medical_pricelist.models import (
    ItemsPricelist,
    ServicesPricelist,
    ServicesPricelistDetail,
    ItemsPricelistDetail
)


def create_test_item_pricelist(location_id, custom_props={}):
    return ItemsPricelist.objects.create(
        **{
            "name": "test-item-price-list",
            "location_id": location_id,
            "pricelist_date": "2019-01-01",
            "validity_from": "2019-01-01",
            "audit_user_id": -1,
            **custom_props
        }
    )


def create_test_service_pricelist(location_id, custom_props={}):
    return ServicesPricelist.objects.create(
        **{
            "name": "test-item-price-list",
            "location_id": location_id,
            "pricelist_date": "2019-01-01",
            "validity_from": "2019-01-01",
            "audit_user_id": -1,
            **custom_props
        }
    )


def add_service_to_hf_pricelist(service, hf_id=18, custom_props={}):
    hf = HealthFacility.objects.get(pk=hf_id)
    return ServicesPricelistDetail.objects.create(
        **{
            "services_pricelist": hf.services_pricelist,
            "service": service,
            "validity_from": "2019-01-01",
            "audit_user_id": -1,
            **custom_props
        }
    )

def update_pricelist_service_detail_in_hf_pricelist(service_pricelist_detail, custom_props={}):
    service_pricelist_detail.save_history()
    for key, value in custom_props.items():
        if hasattr(service_pricelist_detail, key):
            setattr(service_pricelist_detail, key, value)
    return service_pricelist_detail.save()


def add_item_to_hf_pricelist(item, hf_id=18, custom_props={}):
    hf = HealthFacility.objects.get(pk=hf_id)
    return ItemsPricelistDetail.objects.create(
        **{
            "items_pricelist": hf.items_pricelist,
            "item": item,
            "validity_from": "2019-01-01",
            "audit_user_id": -1,
            **custom_props
        }
    )

def update_pricelist_item_detail_in_hf_pricelist(item_pricelist_detail, custom_props={}):
    item_pricelist_detail.save_history()
    for key, value in custom_props.items():
        if hasattr(item_pricelist_detail, key):
            setattr(item_pricelist_detail, key, value)
    return item_pricelist_detail.save()
