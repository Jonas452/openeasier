from django.db import models


class DBConfigRecord(models.Model):
    id = models.AutoField(primary_key=True)
    host = models.CharField(max_length=40)
    port = models.CharField(max_length=40)
    name = models.CharField(max_length=40)
    user_db = models.CharField(max_length=40)
    password_db = models.CharField(max_length=40)
    title = models.CharField(max_length=40)

    DB_TYPES = (
        ('MYSQL', 'MYSQL'),
        ('POSTGRESQL', 'POSTGRESQL'),
    )

    db_type = models.CharField(
        max_length=10,
        choices=DB_TYPES,
    )

    class Meta:
        db_table = 'db_config'
