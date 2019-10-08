import uuid
from django.db import models
from core import fields
from medical import models as medical_models


class ItemPricelist(models.Model):
    id = models.AutoField(db_column='PLItemID', primary_key=True)
    uuid = models.CharField(db_column='PLItemUUID', max_length=36, default=uuid.uuid4, unique = True)
    item_name = models.CharField(db_column='PLItemName', max_length=100)
    pricelist_date = fields.DateField(db_column='DatePL')
    location = models.ForeignKey("location.Location", db_column="LocationId", blank=True, null=True,
                                 on_delete=models.DO_NOTHING, related_name='+')
    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(db_column='ValidityTo', blank=True, null=True)
    legacy_id = models.IntegerField(db_column='LegacyID', blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPLItems'


class ItemPricelistDetail(models.Model):
    id = models.AutoField(db_column='PLItemDetailID', primary_key=True)
    item_pricelist = models.ForeignKey(ItemPricelist, on_delete=models.DO_NOTHING, db_column="PLItemID",
                                       related_name='details')
    item = models.ForeignKey(medical_models.Item, db_column="ItemID", on_delete=models.DO_NOTHING,
                             related_name='pricelist_details')
    price_overrule = models.DecimalField(db_column="PriceOverule", max_digits=18, decimal_places=2, blank=True, null=True)
    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(db_column='ValidityTo', blank=True, null=True)
    legacy_id = models.IntegerField(db_column='LegacyID', blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPLItemsDetail'


class ServicePricelist(models.Model):
    id = models.AutoField(db_column='PLServiceID', primary_key=True)
    uuid = models.CharField(db_column='PLServiceUUID', max_length=36, default=uuid.uuid4, unique = True)
    service_name = models.CharField(db_column='PLServName', max_length=100)
    pricelist_date = fields.DateField(db_column='DatePL')
    location = models.ForeignKey("location.Location", db_column="LocationId", blank=True, null=True,
                                 on_delete=models.DO_NOTHING)
    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(db_column='ValidityTo', blank=True, null=True)
    legacy_id = models.IntegerField(db_column='LegacyID', blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPLServices'


class ServicePricelistDetail(models.Model):
    id = models.AutoField(db_column='PLServiceDetailID', primary_key=True)
    service_pricelist = models.ForeignKey(ServicePricelist, on_delete=models.DO_NOTHING, db_column="PLServiceID",
                                          related_name='details')
    service = models.ForeignKey(medical_models.Service, db_column="ServiceID", on_delete=models.DO_NOTHING,
                                related_name='pricelist_details')
    price_overrule = models.DecimalField(db_column="PriceOverule", max_digits=18, decimal_places=2, blank=True, null=True)
    validity_from = fields.DateTimeField(db_column='ValidityFrom')
    validity_to = fields.DateTimeField(db_column='ValidityTo', blank=True, null=True)
    legacy_id = models.IntegerField(db_column='LegacyID', blank=True, null=True)
    audit_user_id = models.IntegerField(db_column='AuditUserID')
    # row_id = models.BinaryField(db_column='RowID', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblPLServicesDetail'
