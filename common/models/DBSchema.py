from django.db import models


class DBSchema:
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'db_schema'
