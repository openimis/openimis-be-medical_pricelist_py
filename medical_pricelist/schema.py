import graphene
from core import prefix_filterset, filter_validity, ExtendedConnection
from django.conf import settings
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db.models import Q
from .apps import MedicalPricelistConfig
from .models import ItemsPricelist, ItemsPricelistDetail, ServicesPricelist, ServicesPricelistDetail
from location.schema import LocationGQLType


class ItemsPricelistGQLType(DjangoObjectType):
    class Meta:
        model = ItemsPricelist
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'uuid': ['exact'],
            'name': ['exact', 'icontains', 'istartswith'],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection


class ItemsPricelistDetailGQLType(DjangoObjectType):
    class Meta:
        model = ItemsPricelistDetail
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
        }
        connection_class = ExtendedConnection


class ServicesPricelistGQLType(DjangoObjectType):
    class Meta:
        model = ServicesPricelist
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'uuid': ['exact'],
            'name': ['exact', 'icontains', 'istartswith'],
            **prefix_filterset("location__", LocationGQLType._meta.filter_fields),
        }
        connection_class = ExtendedConnection


class ServicesPricelistDetailGQLType(DjangoObjectType):
    class Meta:
        model = ServicesPricelistDetail
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
        }
        connection_class = ExtendedConnection


class PriceCompactGQLType(graphene.ObjectType):
    id = graphene.Int()
    price_overrule = graphene.Decimal()


class PricelistsGQLType(graphene.ObjectType):
    services = graphene.List(PriceCompactGQLType)
    items = graphene.List(PriceCompactGQLType)


def prices(element, parent, child, id, **kwargs):
    list_id = kwargs.get(id)
    if list_id is None:
        return []
    list = element.objects.filter(
        Q(**{parent: list_id, 'price_overrule__isnull': False}),
        *filter_validity(**kwargs)
    )
    return [PriceCompactGQLType(id=getattr(e, child),
                                price_overrule=e.price_overrule)
            for e in list.all()]


class Query(graphene.ObjectType):
    pricelists = graphene.Field(
        PricelistsGQLType,
        services_pricelist_id=graphene.Int(),
        items_pricelist_id=graphene.Int()
    )
    services_pricelists = DjangoFilterConnectionField(
        ServicesPricelistGQLType,
        location_uuid=graphene.String(),
    )
    items_pricelists = DjangoFilterConnectionField(
        ItemsPricelistGQLType,
        location_uuid=graphene.String(),
    )

    def resolve_pricelists(self, info, **kwargs):
        if not info.context.user.has_perms(
                MedicalPricelistConfig.gql_query_pricelists_perms):
            raise PermissionDenied(_("unauthorized"))
        return PricelistsGQLType(
            services=prices(ServicesPricelistDetail,
                            'services_pricelist', 'service_id',
                            'services_pricelist_id',
                            **kwargs),
            items=prices(ItemsPricelistDetail,
                         'items_pricelist', 'item_id',
                         'items_pricelist_id',
                         **kwargs)
        )

    def resolve_services_pricelists(self, info, **kwargs):
        filters = [*filter_validity(**kwargs)]
        location_uuid = kwargs.get('location__uuid')
        if location_uuid is None:
            filters += [Q(location__isnull=True)]
        else:
            filters += [Q(location__uuid=location_uuid)]
        return ServicesPricelist.objects.filter(*filters)

    def resolve_items_pricelists(self, info, **kwargs):
        filters = [*filter_validity(**kwargs)]
        location_uuid = kwargs.get('location__uuid')
        if location_uuid is None:
            filters += [Q(location__isnull=True)]
        else:
            filters += [Q(location__uuid=location_uuid)]
        return ItemsPricelist.objects.filter(*filters)
