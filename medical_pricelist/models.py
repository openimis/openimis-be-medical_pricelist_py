import uuid
from django.db import models
from core import fields
from core.models import VersionedModel, UUIDModel, ObjectMutation, MutationLog
from medical import models as medical_models


class ItemsPricelist(VersionedModel):
    id = models.AutoField(db_column='PLItemID', primary_key=True)
    uuid = models.CharField(db_column='PLItemUUID', max_length=36, default=uuid.uuid4, unique=True)
    name = models.CharField(db_column='PLItemName', max_length=100)
    pricelist_date = fields.DateField(db_column='DatePL')
    location = models.ForeignKey("location.Location", db_column="LocationId", blank=True, null=True,
                                 on_delete=models.DO_NOTHING, related_name='+')
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPLItems'


class ItemsOrServicesPricelistDetailManager(models.Manager):
    def filter(self, *args, **kwargs):
        keys = [x for x in kwargs if "itemsvc" in x]
        for key in keys:
            new_key = key.replace("itemsvc", self.model.model_prefix)
            kwargs[new_key] = kwargs.pop(key)
        return super(ItemsOrServicesPricelistDetailManager, self).filter(*args, **kwargs)


class ItemsOrServicesPricelistDetail:
    objects = ItemsOrServicesPricelistDetailManager()

    class Meta:
        abstract = True


class ItemsPricelistDetail(VersionedModel, ItemsOrServicesPricelistDetail):
    id = models.AutoField(db_column='PLItemDetailID', primary_key=True)
    items_pricelist = models.ForeignKey(ItemsPricelist, on_delete=models.CASCADE, db_column="PLItemID",
                                       related_name='details')
    item = models.ForeignKey(medical_models.Item, db_column="ItemID", on_delete=models.CASCADE,
                             related_name='pricelist_details')
    price_overrule = models.DecimalField(db_column="PriceOverule", max_digits=18, decimal_places=2, blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)
    model_prefix = "item"
    pricelist_field = 'items_pricelist'
    objects = ItemsOrServicesPricelistDetailManager()

    class Meta:
        managed = False
        db_table = 'tblPLItemsDetail'


class ServicesPricelist(VersionedModel):
    id = models.AutoField(db_column='PLServiceID', primary_key=True)
    uuid = models.CharField(db_column='PLServiceUUID', max_length=36, default=uuid.uuid4, unique=True)
    name = models.CharField(db_column='PLServName', max_length=100)
    pricelist_date = fields.DateField(db_column='DatePL')
    location = models.ForeignKey("location.Location", db_column="LocationId", blank=True, null=True,
                                 on_delete=models.DO_NOTHING)
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPLServices'


class ServicesPricelistDetail(VersionedModel, ItemsOrServicesPricelistDetail):
    id = models.AutoField(db_column='PLServiceDetailID', primary_key=True)
    services_pricelist = models.ForeignKey(ServicesPricelist, on_delete=models.CASCADE, db_column="PLServiceID",
                                          related_name='details')
    service = models.ForeignKey(medical_models.Service, db_column="ServiceID", on_delete=models.CASCADE,
                                related_name='pricelist_details')
    price_overrule = models.DecimalField(db_column="PriceOverule", max_digits=18, decimal_places=2, blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)
    model_prefix = "service"
    pricelist_field = 'services_pricelist'

    objects = ItemsOrServicesPricelistDetailManager()

    class Meta:
        managed = False
        db_table = 'tblPLServicesDetail'


class ItemsPricelistMutation(UUIDModel, ObjectMutation):
    pricelist = models.ForeignKey(ItemsPricelist, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='items_pricelists')

    class Meta:
        managed = True
        db_table = "medical_ItemsPricelistMutation"


class ServicesPricelistMutation(UUIDModel, ObjectMutation):
    pricelist = models.ForeignKey(ServicesPricelist, models.DO_NOTHING, related_name='mutations')
    mutation = models.ForeignKey(MutationLog, models.DO_NOTHING, related_name='services_pricelists')

    class Meta:
        managed = True
        db_table = "medical_ServicesPricelistMutation"
