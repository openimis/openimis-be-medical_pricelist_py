from location.models import HealthFacility
from medical_pricelist.models import (
    ItemsPricelist,
    ServicesPricelist,
    ServicesPricelistDetail,
    ItemsPricelistDetail
)


def create_test_item_pricelist(location_id, custom_props=None):
    if custom_props is None:
        custom_props = {}
    else:
        custom_props = {k: v for k, v in custom_props.items() if hasattr(ItemsPricelist, k)}
    obj = ItemsPricelist.objects.create(
        **{
            "name": "test-item-price-list",
            "location_id": location_id,
            "pricelist_date": "2019-01-01",
            "validity_from": "2019-01-01",
            "audit_user_id": 1,
            **custom_props
        }
    )
    return obj


def create_test_service_pricelist(location_id, custom_props=None):
    if custom_props is None:
        custom_props = {}
    else:
        custom_props = {k: v for k, v in custom_props.items() if hasattr(ServicesPricelist, k)}
    obj =  ServicesPricelist.objects.create(
        **{
            "name": "test-item-price-list",
            "location_id": location_id,
            "pricelist_date": "2019-01-01",
            "validity_from": "2019-01-01",
            "audit_user_id": 1,
            **custom_props
        }
    )
    return obj


def add_service_to_hf_pricelist(service, hf_id, custom_props=None):
    hf = HealthFacility.objects.get(pk=hf_id)
    hf_pl = hf.services_pricelist
    if not hf_pl:
        hf_pl = create_test_service_pricelist(hf.location_id)
        hf.update(
            services_pricelist=hf_pl
        )     
    if custom_props is None:
        custom_props = {}
    else:
        custom_props = {k: v for k, v in custom_props.items() if hasattr(ItemsPricelistDetail, k)}         
    obj = ServicesPricelistDetail.objects.filter(
        services_pricelist=hf_pl,
        service=service,
        validity_to__isnull=True
    ).first()
    if obj is not None:
        if custom_props:
            ServicesPricelistDetail.objects.filter(
                services_pricelist=hf_pl,
                service=service,
                validity_to__isnull=True
            ).update(**custom_props)
            obj.refresh_from_db()
        return obj
    else:
        obj = ServicesPricelistDetail.objects.create(
            **{
                "services_pricelist": hf_pl,
                "service": service,
                "validity_from": "2019-01-01",
                "audit_user_id": 1,
                **custom_props
            }
        )
    return obj


def update_pricelist_service_detail_in_hf_pricelist(service_pricelist_detail, custom_props=None):
    service_pricelist_detail.save_history()
    if custom_props is not None:
        for key, value in custom_props.items():
            if hasattr(service_pricelist_detail, key):
                setattr(service_pricelist_detail, key, value)

    return service_pricelist_detail.save()


def add_item_to_hf_pricelist(item, hf_id, custom_props=None):
    hf = HealthFacility.objects.get(pk=hf_id)
    hf_pl = hf.items_pricelist
    if not hf_pl:
        hf_pl = create_test_item_pricelist(hf.location_id)
        HealthFacility.objects.get(pk=hf_id).update(
            items_pricelist=hf_pl
        )
    if custom_props is None:
        custom_props = {}
    else:
        custom_props = {k: v for k, v in custom_props.items() if hasattr(ItemsPricelistDetail, k)}         
    obj = ItemsPricelistDetail.objects.filter(
        items_pricelist=hf_pl,
        item=item,
        validity_to__isnull=True
    ).first()
    if obj is not None:
        if custom_props:
            ItemsPricelistDetail.objects.filter(
                items_pricelist=hf_pl,
                item=item,
                validity_to__isnull=True
            ).update(**custom_props)
            obj.refresh_from_db()
        return obj
    else:
        obj = ItemsPricelistDetail.objects.create(
            **{
                "items_pricelist": hf_pl,
                "item": item,
                "validity_from": "2019-01-01",
                "audit_user_id": 1,
                **custom_props
            }
        )
    return obj


def update_pricelist_item_detail_in_hf_pricelist(item_pricelist_detail, custom_props=None):
    if custom_props is not None:
        item_pricelist_detail.save_history()
        for key, value in custom_props.items():
            if hasattr(item_pricelist_detail, key):
                setattr(item_pricelist_detail, key, value)
    return item_pricelist_detail.save()
