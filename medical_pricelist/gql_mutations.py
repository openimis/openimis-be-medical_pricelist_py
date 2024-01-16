import datetime
from gettext import gettext as _
import graphene
import medical.models
from core.schema import OpenIMISMutation
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError, PermissionDenied
from .apps import MedicalPricelistConfig
from .models import (
    ServicesPricelist,
    ServicesPricelistDetail,
    ItemsPricelist,
    ItemsPricelistDetail,
    ServicesPricelistMutation,
    ItemsPricelistMutation,
)
from .services import set_pricelist_deleted, check_unique_name_items_pricelist, check_unique_name_services_pricelist
from medical.models import Service, Item
from location.models import Location


class DetailPriceOverruleType(graphene.InputObjectType):
    uuid = graphene.UUID(required=True)
    price = graphene.Decimal()


class ItemsOrServicesPricelistInputType(OpenIMISMutation.Input):
    name = graphene.String(required=True)
    pricelist_date = graphene.Date(required=True)
    location_id = graphene.UUID()
    added_details = graphene.List(graphene.NonNull(graphene.UUID))
    removed_details = graphene.List(graphene.NonNull(graphene.UUID))
    price_overrules = graphene.List(graphene.NonNull(DetailPriceOverruleType))


class ServicesPricelistInputType(ItemsOrServicesPricelistInputType):
    pass


def create_or_update_pricelist(
    data, user, pricelist_model, service_or_item_model, detail_model
):
    incoming_name = data['name']
    pricelist_uuid = data.pop("uuid", None)
    current_pricelist = pricelist_model.objects.filter(uuid=pricelist_uuid).first()
    current_name = current_pricelist.name if current_pricelist else None

    if current_name != incoming_name:
        if isinstance(current_pricelist, ServicesPricelist):
            if check_unique_name_services_pricelist(incoming_name):
                raise ValidationError(
                    _("mutation.service_name_duplicated"))
        elif isinstance(current_pricelist, ItemsPricelist):
            if check_unique_name_items_pricelist(incoming_name):
                raise ValidationError(
                    _("mutation.item_name_duplicated"))

    client_mutation_id = data.pop("client_mutation_id", None)
    data.pop("client_mutation_label", None)
    price_overrules = data.pop("price_overrules", None)
    added_details = data.pop("added_details", None)
    removed_details = data.pop("removed_details", None)
    if not data["audit_user_id"]:
        data["audit_user_id"] = user.id_for_audit

    location_uuid = data.pop("location_id", None)
    data["location"] = (
        Location.objects.get(uuid=location_uuid) if location_uuid else None
    )

    if pricelist_uuid:
        pricelist = pricelist_model.objects.get(uuid=pricelist_uuid)
        if pricelist.validity_to:
            raise ValidationError("User can not edit historical data")
        for (key, value) in data.items():
            setattr(pricelist, key, value)
    else:
        pricelist = pricelist_model.objects.create(**data)
    pricelist.save()

    if added_details is not None:
        for uuid in added_details:
            kwargs = {
                # We want to keep the history of items/services present in a pricelist
                "validity_to": None,
                detail_model.pricelist_field: pricelist,
                f"{detail_model.model_prefix}__uuid": uuid,
            }
            detail_model.objects.update_or_create(
                defaults={
                    detail_model.model_prefix: service_or_item_model.objects.get(
                        uuid=uuid
                    ),
                    detail_model.pricelist_field: pricelist,
                    "audit_user_id": data["audit_user_id"],
                },
                **kwargs,
            )

    if removed_details is not None:
        details = pricelist.details.filter(
            itemsvc__uuid__in=removed_details,
            validity_to=None,
        )
        for detail_to_remove in details:
            detail_to_remove.delete_history()

    if price_overrules is not None:
        for overrule in price_overrules:
            detail = pricelist.details.filter(
                itemsvc__uuid=overrule["uuid"],
                validity_to=None,
            ).get()
            # Save history
            if detail:
                detail.save_history()
            detail.validity_from = datetime.datetime.now()
            detail.price_overrule = overrule["price"]
            detail.save()

    if client_mutation_id:
        if isinstance(pricelist, ServicesPricelist):
            ServicesPricelistMutation.object_mutated(
                user,
                client_mutation_id=client_mutation_id,
                pricelist=pricelist,
            )
        elif isinstance(pricelist, ItemsPricelist):
            ItemsPricelistMutation.object_mutated(
                user,
                client_mutation_id=client_mutation_id,
                pricelist=pricelist,
            )

    return pricelist


class CreateOrUpdateItemsOrServicesPricelistMutation(OpenIMISMutation):
    @classmethod
    def do_mutate(cls, perms, user, **data):
        if type(user) is AnonymousUser or not user.id:
            raise ValidationError(_("mutation.authentication_required"))
        if not user.has_perms(perms):
            raise PermissionDenied(_("unauthorized"))

        data["audit_user_id"] = user.id_for_audit

        return create_or_update_pricelist(
            data, user, cls.pricelist_model, cls.service_or_item_model, cls.detail_model
        )


class CreateServicesPricelistMutation(CreateOrUpdateItemsOrServicesPricelistMutation):
    _mutation_module = "medical_pricelist"
    _mutation_class = "CreateServicesPricelistMutation"
    pricelist_model = ServicesPricelist
    service_or_item_model = Service
    detail_model = ServicesPricelistDetail

    class Input(ServicesPricelistInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            cls.do_mutate(
                MedicalPricelistConfig.gql_mutation_pricelists_medical_services_add_perms,
                user,
                **data,
            )
        except Exception as exc:
            return [
                {
                    "message": _("pricelist.mutation.failed_to_create_pricelist")
                    % {"uuid": data["uuid"]},
                    "detail": str(exc),
                }
            ]


class UpdateServicesPricelistMutation(CreateOrUpdateItemsOrServicesPricelistMutation):
    _mutation_module = "medical_pricelist"
    _mutation_class = "UpdateServicesPricelistMutation"
    pricelist_model = ServicesPricelist
    service_or_item_model = Service
    detail_model = ServicesPricelistDetail

    class Input(ServicesPricelistInputType):
        uuid = graphene.UUID(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            cls.do_mutate(
                MedicalPricelistConfig.gql_mutation_pricelists_medical_services_update_perms,
                user,
                **data,
            )
            return None
        except Exception as exc:
            return [
                {
                    "message": _("pricelist.mutation.failed_to_update_pricelist")
                    % {"uuid": data["uuid"]},
                    "detail": str(exc),
                }
            ]


class DeleteServicesPricelistMutation(OpenIMISMutation):
    _mutation_module = "medical_pricelist"
    _mutation_class = "UpdateServicesPricelistMutation"

    class Input(OpenIMISMutation.Input):
        uuids = graphene.List(graphene.UUID)

    @classmethod
    def async_mutate(cls, user, **data):
        if not user.has_perms(
            MedicalPricelistConfig.gql_mutation_pricelists_medical_services_delete_perms
        ):
            raise PermissionDenied(_("Unauthorized"))
        errors = []
        for uuid in data["uuids"]:
            pricelist = ServicesPricelist.objects.filter(uuid=uuid).first()
            if pricelist is None:
                errors.append(
                    {
                        "title": uuid,
                        "list": [
                            {
                                "message": _(
                                    "pricelist.validation.id_does_not_exist",
                                    {"id": uuid},
                                )
                            }
                        ],
                    }
                )
                continue

            errors += set_pricelist_deleted(pricelist)
        if len(errors) == 1:
            errors = errors[0]["list"]
        return errors


class ItemsPricelistInputType(ItemsOrServicesPricelistInputType):
    pass


class CreateItemsPricelistMutation(CreateOrUpdateItemsOrServicesPricelistMutation):
    _mutation_module = "medical_pricelist"
    _mutation_class = "CreateItemsPricelistMutation"
    pricelist_model = ItemsPricelist
    service_or_item_model = Item
    detail_model = ItemsPricelistDetail

    class Input(ItemsPricelistInputType):
        pass

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            cls.do_mutate(
                MedicalPricelistConfig.gql_mutation_pricelists_medical_items_add_perms,
                user,
                **data,
            )
        except Exception as exc:
            return [
                {
                    "message": _("pricelist.mutation.failed_to_create_pricelist")
                    % {"uuid": data["uuid"]},
                    "detail": str(exc),
                }
            ]


class UpdateItemsPricelistMutation(CreateOrUpdateItemsOrServicesPricelistMutation):
    _mutation_module = "medical_pricelist"
    _mutation_class = "UpdateItemsPricelistMutation"
    pricelist_model = ItemsPricelist
    service_or_item_model = Item
    detail_model = ItemsPricelistDetail

    class Input(ItemsPricelistInputType):
        uuid = graphene.UUID(required=True)

    @classmethod
    def async_mutate(cls, user, **data):
        try:
            cls.do_mutate(
                MedicalPricelistConfig.gql_mutation_pricelists_medical_items_update_perms,
                user,
                **data,
            )
            return None
        except Exception as exc:
            return [
                {
                    "message": _("pricelist.mutation.failed_to_update_pricelist")
                    % {"uuid": data["uuid"]},
                    "detail": str(exc),
                }
            ]


class DeleteItemsPricelistMutation(OpenIMISMutation):
    _mutation_module = "medical_pricelist"
    _mutation_class = "UpdateItemsPricelistMutation"

    class Input(OpenIMISMutation.Input):
        uuids = graphene.List(graphene.UUID)

    @classmethod
    def async_mutate(cls, user, **data):
        if not user.has_perms(
            MedicalPricelistConfig.gql_mutation_pricelists_medical_items_delete_perms
        ):
            raise PermissionDenied(_("Unauthorized"))
        errors = []
        for uuid in data["uuids"]:
            pricelist = ItemsPricelist.objects.filter(uuid=uuid).first()
            if pricelist is None:
                errors.append(
                    {
                        "title": uuid,
                        "list": [
                            {
                                "message": _(
                                    "pricelist.validation.id_does_not_exist",
                                    {"id": uuid},
                                )
                            }
                        ],
                    }
                )
                continue

            errors += set_pricelist_deleted(pricelist)
        if len(errors) == 1:
            errors = errors[0]["list"]
        return errors
