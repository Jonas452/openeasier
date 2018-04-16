from datetime import datetime as DateTime

from ckanapi import RemoteCKAN
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import View

from backend.database.DatabaseExtractor import DatabaseExtractor
from backend.database.TableExtractor import TableExtractor
from backend.DataQuality import DataQuality
from common.models import CKANInstance, DBConfig, Resource, ResourceSchedule, DBSchema, DBTable, DBColumn, \
    ResourceDataDictionary, ResourceNotification, PublicationLog
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
        tables = extractor.get_tables_by_words(search, user_schemas)

        for table in tables:
            table_extractor = TableExtractor(db_config, table.get('table_name'), table.get('table_schema'))

            table['verbose_name'] = util.verbose_name(table.get('table_name'))

            table_columns = table_extractor.get_columns(special_columns=False, limit=5)

            verbose_columns = []
            for column in table_columns:
                verbose_columns.append(util.verbose_name(column.get('column_name')))

            table['columns'] = verbose_columns

            table_data_sample = table_extractor.get_data(table_columns, 4)
            table['sample'] = table_data_sample

        PARAMETERS = {
            'search_word': request.POST['search'],
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
        table_columns = table_extractor.get_columns(special_columns=False)

        data = table_extractor.get_data(table_columns, 10)

        if len(table_extractor.get_special_columns()) > 1:
            has_secondary = True
        else:
            has_secondary = False

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
            'has_secondary': has_secondary,
        }

        return render(request, self.template_name, PARAMETERS)


class ResourceCreateView(View):
    template_name = 'frontend/resource_create.html'

    def post(self, request, table_name):
        db_config = DBConfig.objects.get(id=request.POST['database_id'])
        ckan_instance = CKANInstance.objects.get(id=1)

        table_schema = request.POST['table_schema']

        PARAMETERS = dict()

        if request.POST.get('action', False) == 'create':
            table = DBTable()

            table.name = table_name
            table.db_schema = DBSchema.objects.get(name=table_schema)
            table.primary_key = request.POST['primary_key']
            table.save()

            table_extractor = TableExtractor(db_config, table_name, table_schema)
            table_columns = table_extractor.get_columns()

            columns = util.get_items_post(request.POST, 'column_')
            for column in columns:

                temp_column = DBColumn()
                temp_column.name = column
                temp_column.db_table = table

                for table_column in table_columns:
                    if table_column.get('column_name') == column:
                        temp_column.type = table_column.get('data_type')

                        if table_column.get('character_maximum_length') is not None:
                            temp_column.size = table_column.get('character_maximum_length')
                        elif table_column.get('numeric_precision') is not None:
                            temp_column.size = table_column.get('numeric_precision')
                        else:
                            temp_column.size = 0

                        temp_column.not_null = table_column.get('is_nullable')
                        break

                temp_column.save()

            # FK COLUMNS ############
            temp_fks = util.get_items_post(request.POST, 'fk_')
            temp_keys = util.get_items_post(request.POST, 'key_')
            temp_fkeys = util.get_items_post(request.POST, 'fkey_')

            table_fks = list()

            for fk in temp_fks:
                split_str = fk.split('_table_')

                # get the table
                if split_str[1] not in table_fks:
                    table_fks.append(split_str[1])

                    table_split = (split_str[1]).split('_schema_')

                    table_temp = DBTable()
                    table_temp.name = table_split[0]
                    table_temp.db_schema = DBSchema.objects.get(name=table_split[1])
                    table_temp.db_table = table

                    # Search the table's key name
                    for temp_key in temp_keys:
                        ss_key = temp_key.split('_table_')

                        if ss_key[1] == table_temp.name:
                            table_temp.primary_key = ss_key[0]
                            break;

                    # Search the table's fk key name
                    for temp_fkey in temp_fkeys:
                        ss_fkey = temp_fkey.split('_table_')

                        if ss_fkey[1] == table_temp.name:
                            table_temp.fk_name = ss_fkey[0]
                            break;

                    table_temp.save()

                    for t_fk in temp_fks:
                        t_split_str = t_fk.split('_table_')

                        t_table_extractor = TableExtractor(db_config, table_split[0], table_split[1])
                        t_table_columns = t_table_extractor.get_columns()

                        if t_split_str[1] == split_str[1]:
                            temp_column = DBColumn()
                            temp_column.name = t_split_str[0]
                            temp_column.db_table = table_temp

                            for t_table_column in t_table_columns:
                                if t_table_column.get('column_name') == t_split_str[0]:
                                    temp_column.type = t_table_column.get('data_type')

                                    if t_table_column.get('character_maximum_length') is not None:
                                        temp_column.size = t_table_column.get('character_maximum_length')
                                    elif t_table_column.get('numeric_precision') is not None:
                                        temp_column.size = t_table_column.get('numeric_precision')
                                    else:
                                        temp_column.size = 0

                                    temp_column.not_null = t_table_column.get('is_nullable')
                                    break

                            temp_column.save()

            #########################

            resource = Resource()

            resource.name = request.POST['name']
            resource.description = request.POST['description']
            resource.table = table
            resource.ckan = ckan_instance
            resource.resource_status = 'ACTIVE'
            resource.ckan_data_set_id = request.POST['dataset']
            resource.user = request.user

            resource.save()

            messages.success(request, 'Resource created with success!')

            return redirect('frontend:panel_resource')

        elif request.POST.get('action', False) == 'show':
            columns = util.get_items_post(request.POST, 'column_')
            fk_columns = util.get_items_post(request.POST, 'fk_')
            key_columns = util.get_items_post(request.POST, 'key_')
            fkey_columns = util.get_items_post(request.POST, 'fkey_')

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
                'key_columns': key_columns,
                'fkey_columns': fkey_columns,
                'fk_columns': fk_columns,
                'datasets': datasets,
            }

        return render(request, self.template_name, PARAMETERS)

    def get(self, request, table_name):
        return render(request, self.template_name, )


class ResourceScheduleView(View):
    template_name = 'frontend/resource_schedule.html'

    def post(self, request, resource_id):
        resource = Resource.objects.get(id=resource_id)

        datetime_obj = DateTime.strptime(request.POST['schedule_date_time'], '%Y-%m-%d')

        resource.schedule_date_time = datetime_obj
        resource.schedule_type = request.POST['schedule_type']

        resource.save()

        resource_schedule = ResourceSchedule()

        resource_schedule.resource = resource
        resource_schedule.schedule_date_time = datetime_obj
        resource_schedule.execution_status = resource_schedule.STATUS_SCHEDULED

        resource_schedule.save()

        messages.success(request, 'Resource scheduled with success!')

        return redirect('frontend:panel_resource')

    def get(self, request, resource_id):
        resource = Resource.objects.get(id=resource_id)

        PARAMETERS = {
            'resource': resource
        }

        return render(request, self.template_name, PARAMETERS)


class ResourceDataDictionaryView(View):
    template_name = 'frontend/resource_data_dictionary.html'

    def post(self, request, resource_id):

        data_dictionary_id = request.POST['data_dictionary_id']
        if data_dictionary_id:
            data_dictionary = ResourceDataDictionary.objects.get(id=int(data_dictionary_id))
        else:
            data_dictionary = ResourceDataDictionary()

        data_dictionary.resource = Resource.objects.get(id=resource_id)
        data_dictionary.description = request.POST['dd_description']

        data_dictionary.save()

        columns_id = util.get_items_post(request.POST, 'column_')

        for column in columns_id:
            temp_column = DBColumn.objects.get(id=column)
            temp_column.dd_description = request.POST['column_' + str(column)]
            temp_column.save()

        messages.success(request, 'Resource Data Dictionary created with success!')

        return redirect('frontend:panel_resource')

    def get(self, request, resource_id):
        resource = Resource.objects.get(id=resource_id)

        try:
            data_dictionary = ResourceDataDictionary.objects.get(resource=resource)
        except Exception:
            data_dictionary = None

        data = DBColumn.objects.filter(db_table=resource.table)

        columns = list()

        for item in data:
            column = {
                'id': item.id,
                'name': item.name,
                'dd_description': item.dd_description,
                'verbose_name': util.verbose_name(item.name)
            }
            columns.append(column)

        for temp_table in DBTable.objects.filter(db_table=resource.table):
            data_fk = DBColumn.objects.filter(db_table=temp_table)

            for item in data_fk:
                column = {
                    'id': item.id,
                    'name': item.name,
                    'dd_description': item.dd_description,
                    'verbose_name': util.verbose_name(temp_table.name) + " - " + util.verbose_name(item.name)
                }
                columns.append(column)

        PARAMETERS = {
            'resource': resource,
            'data_dictionary': data_dictionary,
            'columns': columns,
        }

        return render(request, self.template_name, PARAMETERS)


class ResourceSecondaryColumnsView(View):
    template_name = 'frontend/resource_secondary_columns.html'

    def post(self, request, table_name):
        db_config = DBConfig.objects.get(id=request.POST['database_id'])
        table_schema = request.POST['table_schema']

        table_extractor = TableExtractor(db_config, table_name, table_schema)

        fk_tables = table_extractor.get_special_columns(only_fk=True);

        tables = list()

        for fk_table in fk_tables:

            temp_table_extractor = TableExtractor(db_config, fk_table.get('table_name'), fk_table.get('table_schema'))
            table_columns = temp_table_extractor.get_columns(special_columns=False)
            data = temp_table_extractor.get_data(table_columns, 5)

            columns = list()

            for table_column in table_columns:
                column = {
                    'name': table_column.get('column_name'),
                    'verbose_name': util.verbose_name(table_column.get('column_name'))
                }
                columns.append(column)

            table = {
                'table_name': fk_table.get('table_name'),
                'table_name_verbose': util.verbose_name(fk_table.get('table_name')),
                'table_schema': fk_table.get('table_schema'),
                'table_primary_key': temp_table_extractor.get_primary_key_name(),
                'table_fk_column': fk_table.get('column_name'),
                'columns': columns,
                'data': data,
            }
            tables.append(table)

        PARAMETERS = {
            'database': db_config,
            'table_name': table_name,
            'table_schema': table_schema,
            'tables': tables,
            'primary_key': request.POST['primary_key'],
            'columns': util.get_items_post(request.POST, 'column_'),
        }

        return render(request, self.template_name, PARAMETERS)

    def get(self, request, table_name):
        return render(request, self.template_name)


class ResourceEditView(View):
    template_name = 'frontend/resource_edit.html'

    def post(self, request, resource_id):
        resource = Resource.objects.get(id=resource_id)

        resource.name = request.POST['name']
        resource.description = request.POST['description']

        resource.save()

        messages.success(request, 'Resource edited with success!')

        return redirect('frontend:panel_resource')

    def get(self, request, resource_id):
        ckan_instance = CKANInstance.objects.get(id=1)
        remote_ckan = RemoteCKAN(ckan_instance.url)
        resource = Resource.objects.get(id=resource_id)
        dataset = remote_ckan.action.package_show(id=resource.ckan_data_set_id)

        PARAMETERS = {
            'resource': resource,
            'dataset': dataset.get('name'),
        }

        return render(request, self.template_name, PARAMETERS)


class ResourceNotificationView(View):
    template_name = 'frontend/resource_notification.html'

    def post(self, request, resource_id):

        resource_notification = ResourceNotification()
        resource_notification.email = request.POST['email']
        resource_notification.resource_id = resource_id

        try:
            resource_notification.save()
            messages.success(request, 'Resource notification saved with success!')
        except Exception:
            messages.error(request, 'Error while saving the resource notification.')

        return redirect('frontend:resource_notification', resource_id)

    def get(self, request, resource_id):
        resource = Resource.objects.get(id=resource_id)

        emails = ResourceNotification.objects.filter(resource=resource)

        PARAMETERS = {
            'resource': resource,
            'emails': emails
        }

        return render(request, self.template_name, PARAMETERS)


class NotificationDeleteView(View):

    def post(self, request, email_id):

        resource_notification = ResourceNotification.objects.get(id=email_id)
        resource_id = resource_notification.resource_id

        try:
            resource_notification.delete()
            messages.success(request, 'Resource notification deleted with success!')
        except Exception:
            messages.error(request, 'Error while deleting the resource notification.')

        return redirect('frontend:resource_notification', resource_id)


class ResourceLogView(View):
    template_name = 'frontend/resource_log.html'

    def get(self, request, resource_id):
        resource = Resource.objects.get(id=resource_id)

        resource_schedule = ResourceSchedule.objects.filter(resource=resource)
        resource_schedule = resource_schedule.exclude(execution_status=ResourceSchedule.STATUS_SCHEDULED)
        resource_schedule = resource_schedule.last()

        logs = PublicationLog.objects.filter(resource_schedule=resource_schedule)

        PARAMETERS = {
            'resource': resource,
            'resource_schedule': resource_schedule,
            'logs': logs
        }

        return render(request, self.template_name, PARAMETERS)

class ResourceDataQualityAssessmentView(View):
    template_name = 'frontend/resource_data_quality_assessment.html'

    def post(self, request, resource_id):
        return render(request, self.template_name)

    def get(self, request, resource_id):
        resource = Resource.objects.get(id=resource_id)

        resource_schedule = ResourceSchedule.objects.filter(resource=resource)
        resource_schedule = resource_schedule.exclude(execution_status=ResourceSchedule.STATUS_SCHEDULED)
        resource_schedule = resource_schedule.last()

        data_quality = DataQuality(resource_id)

        PARAMETERS = {
            'resource': resource,
            'resource_schedule': resource_schedule,
            'columns_missing_data': data_quality.columns_missing_data_(),
            'columns_format_consistency': data_quality.columns_format_consistency(),
        }

        return render(request, self.template_name, PARAMETERS)

