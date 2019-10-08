import graphene
from core import filter_validity, ExtendedConnection
from graphene_django import DjangoObjectType
from django.db.models import Q
from .models import ItemPricelist, ItemPricelistDetail, ServicePricelist, ServicePricelistDetail


class ItemPricelistGQLType(DjangoObjectType):
    class Meta:
        model = ItemPricelist
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'uuid': ['exact'],
            'item_name': ['exact', 'icontains', 'istartswith'],
        }
        connection_class = ExtendedConnection


class ItemPricelistDetailGQLType(DjangoObjectType):
    class Meta:
        model = ItemPricelistDetail
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
        }
        connection_class = ExtendedConnection


class ServicePricelistGQLType(DjangoObjectType):
    class Meta:
        model = ServicePricelist
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'uuid': ['exact'],
            'service_name': ['exact', 'icontains', 'istartswith'],
        }
        connection_class = ExtendedConnection


class ServicePricelistDetailGQLType(DjangoObjectType):
    class Meta:
        model = ServicePricelistDetail
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
        service_pricelist_id=graphene.Int(),
        item_pricelist_id=graphene.Int()
    )

    def resolve_pricelists(self, info, **kwargs):
        return PricelistsGQLType(
            services=prices(ServicePricelistDetail,
                            'service_pricelist', 'service_id',
                            'service_pricelist_id',
                            **kwargs),
            items=prices(ItemPricelistDetail,
                         'item_pricelist', 'item_id',
                         'item_pricelist_id',
                         **kwargs)
        )
