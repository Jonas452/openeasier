from django.db import models


class CKANInstance:
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'ckan_instance'
