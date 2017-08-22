from django.db import models


class DBIgnoreRecord(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)

    db_config = models.ForeignKey(
        'DBIgnoreRecord',
        on_delete=models.PROTECT,
    )

    TYPES_TO_IGNORE = (
        ('TABLE', 'TABLE'),
        ('FIELD', 'FIELD'),
        ('SUFFIX', 'SUFFIX'),
    )

    ignore_type = models.CharField(
        max_length=6,
        choices=TYPES_TO_IGNORE,
    )

    class Meta:
        db_table = 'db_ignore'
