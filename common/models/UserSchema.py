from django.db import models


class UserSchema:
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'user_schema'
