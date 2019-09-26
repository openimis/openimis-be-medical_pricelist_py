import graphene
from core import filter_validity, ExtendedConnection
from graphene_django import DjangoObjectType
from .models import ItemPricelist, ItemPricelistDetail, ServicePricelist, ServicePricelistDetail


class ItemPricelistGQLType(DjangoObjectType):
    class Meta:
        model = ItemPricelist
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
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


class Query(graphene.ObjectType):
    pricelists = graphene.Field(
        PricelistsGQLType,
        service_pricelist_id=graphene.Int(),
        item_pricelist_id=graphene.Int()
    )

    def resolve_pricelists(self, info, **kwargs):
        return PricelistsGQLType(
            services=[],
            items=[]
        )
