from django.db import models


class DBTable:
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'db_table'
