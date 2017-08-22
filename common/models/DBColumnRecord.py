from django.db import models


class DBColumnRecord(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)

    db_table = models.ForeignKey(
        'DBTableRecord',
        on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'db_column'
