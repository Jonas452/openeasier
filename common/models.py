from django.db import models


class CKANInstance(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(
        max_length=100,
        help_text='A suggestive name for the CKAN isntance',
    )

    url = models.CharField(
        max_length=200,
        help_text='The URL of the CKAN instance',
        verbose_name='URL', )

    API_CHOICES = (
        ('3', '3'),
    )

    api_version = models.CharField(
        max_length=20,
        choices=API_CHOICES,
        default=3,
        verbose_name='API Version',
        help_text='The version of the CKAN API',
    )

    class Meta:
        db_table = 'ckan_instance'
        verbose_name = 'CKAN Instance'


class DBColumn(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)

    db_table = models.ForeignKey(
        'DBTable',
        on_delete=models.PROTECT,
    )

    class Meta:
        db_table = 'db_column'
        verbose_name = 'Column'


class DBConfig(models.Model):
    id = models.AutoField(primary_key=True)

    host = models.CharField(max_length=40)
    port = models.CharField(max_length=40)
    name = models.CharField(max_length=40)

    user_db = models.CharField(
        max_length=40,
        verbose_name='User',
        help_text='Do not inform an admin user. It is recommended to create an user only with visualization permissions'
    )

    password_db = models.CharField(max_length=40, verbose_name='Password')

    title = models.CharField(
        max_length=40,
        help_text='A suggestive title for the database, making possible the non-IT technician recognize the database',
    )

    DB_TYPES = (
        ('MYSQL', 'MYSQL'),
        ('POSTGRESQL', 'POSTGRESQL'),
    )

    db_type = models.CharField(
        max_length=10,
        choices=DB_TYPES,
        verbose_name='Type'
    )

    def __str__(self):
        return self.title + ' - ' + self.host

    class Meta:
        db_table = 'db_config'
        verbose_name = 'Database Configuration'


class DBIgnore(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)

    db_config = models.ForeignKey(
        'DBConfig',
        on_delete=models.PROTECT,
        verbose_name='Database'
    )

    TYPES_TO_IGNORE = (
        ('TABLE', 'TABLE'),
        ('COLUMN', 'COLUMN'),
        ('SUFFIX', 'SUFFIX'),
    )

    ignore_type = models.CharField(
        max_length=6,
        choices=TYPES_TO_IGNORE,
    )

    class Meta:
        db_table = 'db_ignore'
        verbose_name = 'Ignore'


class DBSchema(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)

    db_config = models.ForeignKey(
        'DBConfig',
        models.PROTECT,
    )

    class Meta:
        db_table = 'db_schema'
        verbose_name = 'Schema'


class DBTable(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)

    db_schema = models.ForeignKey(
        'DBSchema',
        models.PROTECT,
    )

    db_table = models.ForeignKey(
        'self',
        models.PROTECT,
        null=True,
    )

    class Meta:
        db_table = 'db_table'
        verbose_name = 'Table'


class UserSchema(models.Model):
    id = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'user_schema'
        verbose_name = 'User Schema'
