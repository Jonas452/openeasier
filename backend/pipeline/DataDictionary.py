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

from common.models import Resource, DBColumn


class DataDicionary:
    def __init__(self, resource):
        self.resource = resource
        self.table = resource.table

        self.parcial_path = 'working/' + self.table.name

    def pre_run(self):
        # TODO Check if there is a data dictionary already
        pass

    def run(self):
        file = self.parcial_path + "/dictionary_" + self.table.name + ".pdf"
        doc = SimpleDocTemplate(file, pagesize=landscape(A4))

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
            story.append(Paragraph('DIÁRIAMENTE', styles['Normal']))
        elif self.resource.schedule_type == Resource.TYPE_WEEK:
            story.append(Paragraph('SEMANALMENTE', styles['Normal']))
        elif self.resource.schedule_type == Resource.TYPE_MONTH:
            story.append(Paragraph('MENSALMENTE', styles['Normal']))
        elif self.resource.schedule_type == Resource.TYPE_YEAR:
            story.append(Paragraph('ANUALMENTE', styles['Normal']))

        story.append(Spacer(1, 10))

        story.append(Paragraph('<b>DESCRIÇÃO:</b>', styles['Normal']))

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

            data.append([column.name, column.type.upper(), tamanho, aceita_nulo, ''])

        table = Table(data, colWidths=(60*mm, 50*mm, 25*mm, 30*mm, 80*mm))

        table_style = TableStyle()
        table_style.add('BOX', (0, 0), (-1, -1), 0.50, colors.black)
        table_style.add('INNERGRID', (0, 0), (-1, -1), 0.50, colors.black)
        table_style.add('FONTNAME', (0, 0), (-1, 0), 'Times-Bold')
        table_style.add('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
        table_style.add('ALIGNMENT', (2, 1), (-1, -1), 'CENTER')

        table.setStyle(table_style)

        story.append(table)

        doc.build(story)

    def pos_run(self):
        pass
