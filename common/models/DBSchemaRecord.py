from django.db import models


class DBSchemaRecord(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)

    db_config = models.ForeignKey(
        'DBConfigRecord',
        models.PROTECT,
    )

    class Meta:
        db_table = 'db_schema'
