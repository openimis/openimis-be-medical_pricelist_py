from location.models import HealthFacility
from medical_pricelist.models import ServicesPricelistDetail


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
