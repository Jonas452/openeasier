from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class CKANInstance(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(
        max_length=100,
        help_text='A suggestive name for the CKAN instance',
    )

    url = models.CharField(
        max_length=200,
        help_text='The URL of the CKAN instance',
        verbose_name='URL', )

    VERSION_3 = '3'

    API_CHOICES = (
        (VERSION_3, '3'),
    )

    api_version = models.CharField(
        max_length=20,
        choices=API_CHOICES,
        default=VERSION_3,
        verbose_name='API Version',
        help_text='The version of the CKAN API',
    )

    def __str__(self):
        return self.name + ' - ' + self.url

    class Meta:
        db_table = 'ckan_instance'
        verbose_name = 'CKAN Instance'


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

    DB_MYSQL = 'MYSQL'
    DB_POSTGRESQL = 'POSTGRESQL'

    DB_TYPES = (
        (DB_MYSQL, 'MYSQL'),
        (DB_POSTGRESQL, 'POSTGRESQL'),
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


class DBSchema(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)

    db_config = models.ForeignKey(
        'DBConfig',
        models.PROTECT,
    )

    def __str__(self):
        return self.name + ' - ' + self.db_config.name

    class Meta:
        db_table = 'db_schema'
        verbose_name = 'Schema'


class UserSchema(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        models.PROTECT,
    )

    schema = models.ForeignKey(
        'DBSchema',
        models.PROTECT,
        null=True,
    )

    class Meta:
        db_table = 'user_schema'
        verbose_name = 'User Schema'


class UserCkanKey(models.Model):
    ckan_key = models.CharField(
        max_length=200,
        verbose_name='CKAN Key',
    )
    user = models.OneToOneField(
        User,
        models.PROTECT,
        primary_key=True
    )

    class Meta:
        db_table = 'user_ckan_key'
        verbose_name = 'User CKAN Key'


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Resource(TimeStampedModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=250)
    resource_status = models.CharField(max_length=20)
    ckan_data_set_id = models.CharField(max_length=100)
    ckan_resource_id = models.CharField(max_length=100)

    ckan = models.ForeignKey(
        'CKANInstance',
        models.PROTECT
    )

    table = models.ForeignKey(
        'DBTable',
        models.PROTECT
    )

    user = models.ForeignKey(
        User,
        models.PROTECT
    )

    schedule_date_time = models.DateField()

    TYPE_DAY = 'DAY'
    TYPE_WEEK = 'WEEK'
    TYPE_MONTH = 'MONTH'
    TYPE_YEAR = 'YEAR'

    SCHEDULE_TYPES = (
        (TYPE_DAY, 'EVERY DAY'),
        (TYPE_WEEK, 'EVERY WEEK'),
        (TYPE_MONTH, 'EVERY MONTH'),
        (TYPE_YEAR, 'EVERY YEAR'),
    )

    schedule_type = models.CharField(
        max_length=15,
        choices=SCHEDULE_TYPES,
    )

    def resource_url(self):
        return self.ckan.url + '/dataset/' + self.ckan_data_set_id + '/resource/' + self.ckan_resource_id

    def get_last_schedule(self):
        return ResourceSchedule.objects.filter(resource=self).latest('schedule_date_time')

    def get_last_success_schedule(self):
        query = ResourceSchedule.objects.filter(resource=self)
        query = query.filter(execution_status=ResourceSchedule.STATUS_FINISHED)
        return query.latest('schedule_date_time')

    class Meta:
        db_table = 'resource'


class ResourceSchedule(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    schedule_date_time = models.DateField()

    STATUS_SCHEDULED = 'SCHEDULED'
    STATUS_FINISHED = 'FINISHED'
    STATUS_RUNNING = 'RUNNING'
    STATUS_FAILED = 'FAILED'

    STATUS_TYPES = (
        (STATUS_SCHEDULED, 'SCHEDULED'),
        (STATUS_FINISHED, 'FINISHED'),
        (STATUS_RUNNING, 'RUNNING'),
        (STATUS_FAILED, 'FAILED'),
    )

    execution_status = models.CharField (
            max_length=12,
            choices=STATUS_TYPES,
            default=STATUS_SCHEDULED
        )

    resource = models.ForeignKey(
        'Resource',
        models.PROTECT,
    )

    class Meta:
        db_table = 'resource_schedule'


class DBTable(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    primary_key = models.CharField(max_length=20)

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


class DBColumn(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    type = models.CharField(max_length=30)
    size = models.IntegerField()
    not_null = models.CharField(max_length=3)

    db_table = models.ForeignKey(
        'DBTable',
        on_delete=models.PROTECT,
    )

    class Meta:
        db_table = 'db_column'
        verbose_name = 'Column'


class DBIgnore(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)

    db_config = models.ForeignKey(
        'DBConfig',
        on_delete=models.PROTECT,
        verbose_name='Database'
    )

    TYPE_TABLE = 'TABLE'
    TYPE_COLUMN = 'COLUMN'
    TYPE_SUFFIX = 'SUFFIX'

    TYPES_TO_IGNORE = (
        (TYPE_TABLE, 'TABLE'),
        (TYPE_COLUMN, 'COLUMN'),
        (TYPE_SUFFIX, 'SUFFIX'),
    )

    ignore_type = models.CharField(
        max_length=6,
        choices=TYPES_TO_IGNORE,
    )

    class Meta:
        db_table = 'db_ignore'
        verbose_name = 'Ignore'
