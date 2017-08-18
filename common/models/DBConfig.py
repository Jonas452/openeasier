from django.db import models


class DBConfig:
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'db_config'
