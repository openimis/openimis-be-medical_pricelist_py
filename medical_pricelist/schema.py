import graphene
from core import ExtendedConnection
from graphene_django import DjangoObjectType

from .models import PricelistItem, PricelistItemDetail, PricelistService, PricelistServiceDetail


class PricelistItemGQLType(DjangoObjectType):
    class Meta:
        model = PricelistItem
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'item_name': ['exact', 'icontains', 'istartswith'],
        }
        connection_class = ExtendedConnection


class PricelistItemDetailGQLType(DjangoObjectType):
    class Meta:
        model = PricelistItemDetail
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
        }
        connection_class = ExtendedConnection


class PricelistServiceGQLType(DjangoObjectType):
    class Meta:
        model = PricelistService
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
            'service_name': ['exact', 'icontains', 'istartswith'],
        }
        connection_class = ExtendedConnection


class PricelistServiceDetailGQLType(DjangoObjectType):
    class Meta:
        model = PricelistServiceDetail
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'id': ['exact'],
        }
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    pass
