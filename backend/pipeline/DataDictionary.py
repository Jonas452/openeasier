import os
import django
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import mm

os.environ["DJANGO_SETTINGS_MODULE"] = 'openeasier.settings'
django.setup()

from common.models import Resource, DBColumn, DBTable, ResourceDataDictionary


class DataDictionary:
    def __init__(self, resource, my_ckan):
        self.resource = resource
        self.my_ckan = my_ckan
        self.data_dictionary = ResourceDataDictionary.objects.get(resource=resource)
        self.table = resource.table

        self.parcial_path = 'working/' + self.table.name

    def pre_run(self):
        # TODO Check if there is a data dictionary already
        pass

    def run(self):
        self.create_dictionary()
        self.upload_dictionary()

    def create_dictionary(self):
        self.file = self.parcial_path + "/dictionary_" + self.table.name + ".pdf"
        doc = SimpleDocTemplate(self.file, pagesize=landscape(A4))

        story = list()

        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name='CustomTitle',
                fontName='Times-Bold',
                fontSize=14,
                alignment=TA_CENTER,
                textColor=colors.black,
            )
        )

        # Title
        title = "DICIONÁRIO DE DADOS"
        story.append(Paragraph(title, styles['CustomTitle']))
        story.append(Spacer(1, 48))

        # Basic Info
        story.append(Paragraph("<b>RECURSO: </b>", styles['Normal']))
        story.append(Spacer(1, 4))
        story.append(Paragraph(self.resource.name, styles['Normal']))
        story.append(Spacer(1, 10))

        story.append(Paragraph("<b>FREQUÊNCIA DE ATUALIZAÇÃO: </b>", styles['Normal']))
        story.append(Spacer(1, 4))

        if self.resource.schedule_type == Resource.TYPE_DAY:
            story.append(Paragraph('DIARIAMENTE', styles['Normal']))
        elif self.resource.schedule_type == Resource.TYPE_WEEK:
            story.append(Paragraph('SEMANALMENTE', styles['Normal']))
        elif self.resource.schedule_type == Resource.TYPE_MONTH:
            story.append(Paragraph('MENSALMENTE', styles['Normal']))
        elif self.resource.schedule_type == Resource.TYPE_YEAR:
            story.append(Paragraph('ANUALMENTE', styles['Normal']))

        story.append(Spacer(1, 10))

        story.append(Paragraph('<b>DESCRIÇÃO:</b>', styles['Normal']))
        story.append(Paragraph(self.data_dictionary.description, styles['Normal']))

        story.append(Spacer(1, 6))

        # TABLE

        # Table Title
        story.append(Spacer(1, 48))

        # Table Data
        data = [
            ['COLUNA', 'TIPO', 'TAMANHO', 'ACEITA NULO', 'DESCRIÇÃO'],
        ]

        for column in DBColumn.objects.filter(db_table=self.table).order_by('id'):

            aceita_nulo = 'NÃO'
            if column.not_null == 'YES':
                aceita_nulo = 'SIM'

            tamanho = ''
            if column.size > 0:
                tamanho = column.size

            data.append([column.name, column.type.upper(), tamanho, aceita_nulo, column.dd_description])

        for temp_table in DBTable.objects.filter(db_table=self.table):
            for column in DBColumn.objects.filter(db_table=temp_table).order_by('id'):

                aceita_nulo = 'NÃO'
                if column.not_null == 'YES':
                    aceita_nulo = 'SIM'

                tamanho = ''
                if column.size > 0:
                    tamanho = column.size

                data.append([temp_table.name + "_" + column.name, column.type.upper(), tamanho, aceita_nulo,
                             column.dd_description])

        table = Table(data, colWidths=(60 * mm, 50 * mm, 25 * mm, 30 * mm, 80 * mm))

        table_style = TableStyle()
        table_style.add('BOX', (0, 0), (-1, -1), 0.50, colors.black)
        table_style.add('INNERGRID', (0, 0), (-1, -1), 0.50, colors.black)
        table_style.add('FONTNAME', (0, 0), (-1, 0), 'Times-Bold')
        table_style.add('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
        table_style.add('ALIGNMENT', (2, 1), (-1, -1), 'CENTER')

        table.setStyle(table_style)

        story.append(table)

        doc.build(story)

    def upload_dictionary(self):
        if self.data_dictionary.ckan_resource_id:
            self.resource_published = self.my_ckan.action.resource_update(
                id=self.data_dictionary.ckan_resource_id,
                name=self.resource.name + " - Data Dictionary",
                description=self.data_dictionary.description,
                upload=open(self.file, 'rb')
            )
        else:
            self.resource_published = self.my_ckan.action.resource_create(
                package_id=self.resource.ckan_data_set_id,
                name=self.resource.name + " - Data Dictionary",
                description=self.data_dictionary.description,
                upload=open(self.file, 'rb')
            )

    def set_dictionary_resource_id(self):
        self.data_dictionary.ckan_resource_id = self.resource_published.get('id')
        self.data_dictionary.save()

    def pos_run(self):
        self.set_dictionary_resource_id()
