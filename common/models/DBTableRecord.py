from django.db import models


class DBTableRecord(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)

    db_schema = models.ForeignKey(
        'DBSchemaRecord',
        models.PROTECT,
    )

    db_table = models.ForeignKey(
        'self',
        models.PROTECT,
        null=True,
    )

    class Meta:
        db_table = 'db_table'
