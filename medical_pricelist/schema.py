import graphene
from core import ExtendedConnection
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


class Query(graphene.ObjectType):
    pass
