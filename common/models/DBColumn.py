from django.db import models


class DBColumn:
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'db_column'
