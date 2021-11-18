import graphene
from core import prefix_filterset, filter_validity, ExtendedConnection
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Q
from .apps import MedicalPricelistConfig
from medical.schema import ServiceGQLType
from .models import (
    ItemsPricelist,
    ItemsPricelistDetail,
    ServicesPricelist,
    ServicesPricelistDetail,
)
from .gql_mutations import (
    CreateServicesPricelistMutation,
    UpdateServicesPricelistMutation,
    DeleteServicesPricelistMutation,
    CreateItemsPricelistMutation,
    UpdateItemsPricelistMutation,
    DeleteItemsPricelistMutation,
)
from location.schema import LocationGQLType
import graphene_django_optimizer as gql_optimizer


ServiceGQLType.fields = ["id", "name"]


class ItemsPricelistGQLType(DjangoObjectType):
    class Meta:
        model = ItemsPricelist
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "uuid": ["exact"],
            "name": ["exact", "icontains", "istartswith"],
            "location": ["isnull"],
            "pricelist_date": ["exact", "gt", "gte", "lt", "lte"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection


class ItemsPricelistDetailGQLType(DjangoObjectType):
    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(validity_to=None)

    class Meta:
        model = ItemsPricelistDetail
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "items_pricelist": ["exact"],
        }
        connection_class = ExtendedConnection


class ServicesPricelistGQLType(DjangoObjectType):
    class Meta:
        model = ServicesPricelist
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "id": ["exact"],
            "uuid": ["exact"],
            "name": ["exact", "icontains", "istartswith"],
            "location": ["isnull"],
            "pricelist_date": ["exact", "gt", "gte", "lt", "lte"],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection


class ServicesPricelistDetailGQLType(DjangoObjectType):
    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.filter(validity_to=None)

    class Meta:
        model = ServicesPricelistDetail
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "services_pricelist": ["exact"],
        }
        connection_class = ExtendedConnection


class PriceCompactGQLType(graphene.ObjectType):
    id = graphene.Int()
    p = graphene.Decimal()


class PricelistsGQLType(graphene.ObjectType):
    services = graphene.List(PriceCompactGQLType)
    items = graphene.List(PriceCompactGQLType)


def prices(element, parent, child, id, **kwargs):
    list_id = kwargs.get(id)
    if list_id is None:
        return []
    list = element.objects.filter(Q(**{parent: list_id}), *filter_validity(**kwargs))
    return [
        PriceCompactGQLType(id=getattr(e, child), p=e.price_overrule)
        for e in list.all()
    ]


class Query(graphene.ObjectType):
    pricelists = graphene.Field(
        PricelistsGQLType,
        services_pricelist_id=graphene.Int(),
        items_pricelist_id=graphene.Int(),
    )
    services_pricelists = DjangoFilterConnectionField(
        ServicesPricelistGQLType,
        show_history=graphene.Boolean(),
        location_uuid=graphene.String(),
    )
    items_pricelists = DjangoFilterConnectionField(
        ItemsPricelistGQLType,
        show_history=graphene.Boolean(),
        location_uuid=graphene.String(),
    )

    def resolve_pricelists(self, info, services_pricelist_id=None, items_pricelist_id=None, **kwargs):
        # When the caller requests a list of pricelists, they're filtered downstream. When they request a specific PL,
        # and don't have the right to browse all pricelists, we need to verify that they do have access to that PL
        if services_pricelist_id or items_pricelist_id:
            hf = info.context.user.get_health_facility()
            if services_pricelist_id and not info.context.user.has_perms(
                MedicalPricelistConfig.gql_query_pricelists_medical_services_perms
            ):
                if hf and hf.services_pricelist_id != services_pricelist_id:
                    raise PermissionDenied(_("unauthorized"))
            if items_pricelist_id and not info.context.user.has_perms(
                MedicalPricelistConfig.gql_query_pricelists_medical_items_perms
            ):
                if hf and hf.items_pricelist_id != items_pricelist_id:
                    raise PermissionDenied(_("unauthorized"))

        return PricelistsGQLType(
            services=prices(
                ServicesPricelistDetail,
                "services_pricelist",
                "service_id",
                "services_pricelist_id",
                **kwargs
            ),
            items=prices(
                ItemsPricelistDetail,
                "items_pricelist",
                "item_id",
                "items_pricelist_id",
                **kwargs
            ),
        )

    def resolve_services_pricelists(self, info, **kwargs):
        if not info.context.user.has_perms(
            MedicalPricelistConfig.gql_query_pricelists_medical_services_perms
        ):
            raise PermissionDenied(_("unauthorized"))
        filters = []
        show_history = kwargs.get("show_history", False)
        if not show_history:
            filters = [*filter_validity(**kwargs)]

        location_uuid = kwargs.get("location__uuid")
        if location_uuid is not None:
            filters += [
                Q(location__uuid=location_uuid)
                | Q(location__parent__uuid=location_uuid)
            ]
        query = ServicesPricelist.objects.filter(*filters).order_by("name")
        return gql_optimizer.query(query.all(), info)

    def resolve_items_pricelists(self, info, **kwargs):
        if not info.context.user.has_perms(
            MedicalPricelistConfig.gql_query_pricelists_medical_items_perms
        ):
            raise PermissionDenied(_("unauthorized"))
        filters = []
        show_history = kwargs.get("show_history", False)
        if not show_history:
            filters = [*filter_validity(**kwargs)]

        location_uuid = kwargs.get("location__uuid")
        if location_uuid is not None:
            filters += [
                Q(location__uuid=location_uuid)
                | Q(location__parent__uuid=location_uuid)
            ]
        query = ItemsPricelist.objects.filter(*filters).order_by("name")
        return gql_optimizer.query(query.all(), info)


class Mutation(graphene.ObjectType):
    create_services_pricelist = CreateServicesPricelistMutation.Field()
    update_services_pricelist = UpdateServicesPricelistMutation.Field()
    delete_services_pricelist = DeleteServicesPricelistMutation.Field()

    create_items_pricelist = CreateItemsPricelistMutation.Field()
    update_items_pricelist = UpdateItemsPricelistMutation.Field()
    delete_items_pricelist = DeleteItemsPricelistMutation.Field()
