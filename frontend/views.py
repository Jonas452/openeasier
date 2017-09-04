from datetime import datetime as DateTime

from ckanapi import RemoteCKAN
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View

from backend.Scheduler import Scheduler
from backend.database.DatabaseExtractor import DatabaseExtractor
from backend.database.TableExtractor import TableExtractor
from backend.pipeline.Pipeline import Pipeline
from common.models import CKANInstance, DBConfig, Resource, ResourceSchedule, DBSchema, DBTable, DBColumn
from frontend.utils import util, util_search


class ResourcePanelView(View):
    template_name = 'frontend/resource_panel.html'

    def get(self, request):
        resources = Resource.objects.filter(resource_status='ACTIVE')

        resources_results = (
            {
                'type': 'FINISHED',
                'value': ResourceSchedule.objects.filter(execution_status=ResourceSchedule.STATUS_FINISHED).count(),
            },
            {
                'type': 'FAILED',
                'value': ResourceSchedule.objects.filter(execution_status=ResourceSchedule.STATUS_FAILED).count(),
            },
            {
                'type': 'SCHEDULED',
                'value': ResourceSchedule.objects.filter(execution_status=ResourceSchedule.STATUS_SCHEDULED).count(),
            },
            {
                'type': 'RUNNING',
                'value': ResourceSchedule.objects.filter(execution_status=ResourceSchedule.STATUS_RUNNING).count(),
            },
        )

        PARAMETERS = {
            'resources': resources,
            'resources_results': resources_results,
        }

        return render(request, self.template_name, PARAMETERS)

    def post(self, request):
        return render(request, self.template_name, )


class ResourceSearchView(View):
    template_name = 'frontend/resource_search.html'

    def post(self, request):
        search = util_search.create_search_list(request.POST['search'])
        db_config = DBConfig.objects.get(id=request.POST['database_id'])

        user_databases = self.get_user_databases(request.user)
        user_schemas = DBSchema.objects.filter(userschema__user_id=request.user.id)

        extractor = DatabaseExtractor(db_config)
        tables = extractor.extract_tables(search, user_schemas) #TODO GET ALL TABLE AND TREAT NAMES WITH SEARCH_LIST

        for table in tables:
            table_extractor = TableExtractor(db_config, table.get('table_name'), table.get('table_schema'))

            table['verbose_name'] = util.verbose_name(table.get('table_name'))

            table_columns = table_extractor.get_columns(special_columns=False, limit=3)

            verbose_columns = []
            for column in table_columns:
                verbose_columns.append(util.verbose_name(column))

            table['columns'] = verbose_columns

            table_data_sample = table_extractor.get_data(table_columns, 2)
            table['sample'] = table_data_sample

        PARAMETERS = {
            'search': search,
            'user_databases': user_databases,
            'database': db_config,
            'tables': tables,
        }

        return render(request, self.template_name, PARAMETERS, )

    def get(self, request):
        user_databases = self.get_user_databases(request.user)
        return render(request, self.template_name, {'user_databases': user_databases})

    def get_user_databases(self, user):
        schemas = DBSchema.objects.filter(userschema__user_id=user.id)
        return DBConfig.objects.filter(id__in=schemas.values('db_config_id'))


class ResourceColumnsView(View):
    template_name = 'frontend/resource_columns.html'

    def post(self, request, table_name):
        db_config = DBConfig.objects.get(id=request.POST['database_id'])
        table_schema = request.POST['table_schema']

        table_extractor = TableExtractor(db_config, table_name, table_schema)
        table_columns = table_extractor.get_columns(special_columns=False, limit=3)

        data = table_extractor.get_data(table_columns, 5)

        columns = list()
        for item in data[0]:
            column = {
                'name': item,
                'verbose_name': util.verbose_name(item)
            }
            columns.append(column)

        PARAMETERS = {
            'database': db_config,
            'table_name': table_name,
            'verbose_table_name': util.verbose_name(table_name),
            'table_schema': table_schema,
            'primary_key': table_extractor.get_primary_key_name(),
            'columns': columns,
            'data': data,
        }

        return render(request, self.template_name, PARAMETERS)


class ResourceCreateView(View):
    template_name = 'frontend/resource_create.html'

    def post(self, request, table_name):
        db_config = DBConfig.objects.get(id=request.POST['database_id'])
        ckan_instance = CKANInstance.objects.get(id=1)

        table_schema = request.POST['table_schema']

        PARAMETERS = dict()

        if request.POST['action'] == 'create':
            table = DBTable()

            table.name = table_name
            table.db_schema = DBSchema.objects.get(name=table_schema)
            table.primary_key = request.POST['primary_key']
            table.save()

            columns = util.get_items_post(request.POST, 'column_')
            for column in columns:
                temp_column = DBColumn()
                temp_column.name = column
                temp_column.db_table = table
                temp_column.save()

            resource = Resource()

            resource.name = request.POST['name']
            resource.description = request.POST['description']
            resource.table = table
            resource.ckan = ckan_instance
            resource.resource_status = 'ACTIVE'
            resource.ckan_data_set_id = request.POST['dataset']
            resource.user = request.user

            datetime_obj = DateTime.strptime(request.POST['schedule_date_time'], '%Y-%m-%d')

            print(datetime_obj)

            resource.schedule_date_time = datetime_obj
            resource.schedule_type = request.POST['schedule_type']

            resource.save()

            if request.POST['checkbox_publich_now']:
                resource_scheduled = Scheduler.schedule_resource(resource)
                pipeline = Pipeline(ResourceSchedule.objects.get(id=resource_scheduled.id))
                pipeline.execute()

            messages.success(request, 'Resource created with success!')

            return redirect('frontend:panel_resource')

        elif request.POST['action'] == 'show':
            columns = util.get_items_post(request.POST, 'checkbox_')

            remote_ckan = RemoteCKAN(ckan_instance.url)
            datasets = remote_ckan.action.package_list()

            columns_label = ''
            for item in columns:
                columns_label += item + ', '

            columns_label = columns_label[:-2]

            PARAMETERS = {
                'database': db_config,
                'table_name': table_name,
                'columns_label': columns_label,
                'table_schema': table_schema,
                'primary_key': request.POST['primary_key'],
                'columns': columns,
                'datasets': datasets,
            }

        return render(request, self.template_name, PARAMETERS)

    def get(self, request, table_name):
        return render(request, self.template_name, )
