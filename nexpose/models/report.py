import datetime
from enum import Enum
from uuid import uuid4

from lxml.etree import SubElement
from typing import Optional

from nexpose.models import XmlParse, XmlFormat
from nexpose.models.site import Site
from nexpose.types import Element


class ReportScope(Enum):
    global_ = 'global'
    silo = 'silo'


class ReportTemplateSummaryType(Enum):
    """
    lies
     - `jasper` is not documented
    """
    data = 'data'
    document = 'document'

    jasper = 'jasper'


class ReportTemplateSummary(XmlParse):
    def __init__(self, template_id: str, name: str, builtin: bool, scope: ReportScope,
                 template_type: ReportTemplateSummaryType) -> None:
        self.id = template_id
        self.name = name
        self.builtin = builtin
        self.scope = scope
        self.template_type = template_type

    @staticmethod
    def _from_xml(xml: Element) -> 'ReportTemplateSummary':
        assert xml.tag == 'ReportTemplateSummary'

        template_id = xml.attrib.pop('id')
        name = xml.attrib.pop('name')
        builtin = bool(xml.attrib.pop('builtin'))
        scope = ReportScope(xml.attrib.pop('scope'))
        template_type = ReportTemplateSummaryType(xml.attrib.pop('type'))

        return ReportTemplateSummary(template_id=template_id, name=name, builtin=builtin, scope=scope,
                                     template_type=template_type)


class ReportConfigFormat(Enum):
    pdf = 'pdf'
    html = 'html'
    rtf = 'rtf'
    xml = 'xml'
    text = 'text'
    csv = 'csv'
    db = 'db'
    raw_xml = 'raw-xml'
    raw_xml_v2 = 'raw-xml-v2'
    ns_xml = 'ns-xml'
    qualys_xml = 'qualys-xml'


class ReportConfig(XmlFormat):
    def __init__(self, template: ReportTemplateSummary, format: ReportConfigFormat, site: Site, id: int = -1,
                 name: Optional[str] = None) -> None:
        if name is None:
            name = str(uuid4())

        self.template = template
        self.format = format
        self.site = site
        self.id = id
        self.name = name

    def _to_xml(self, root: Element) -> None:
        root.attrib.update({
            'id': str(self.id),
            'name': self.name,
            'template-id': self.template.id,
            'format': self.format.value,
        })

        filter = SubElement(root, 'Filters')
        SubElement(filter, 'filter', attrib={
            'type': 'site',
            'id': str(self.site.id),
        })
        SubElement(root, 'Users')
        SubElement(root, 'Generate')
        SubElement(root, 'Delivery')


class ReportSummaryStatus(Enum):
    started = 'Started'
    generated = 'Generated'
    failed = 'Failed'
    aborted = 'Aborted'
    unknown = 'Unknown'


class ReportSummary(XmlParse):
    def __init__(self, summary_id: Optional[int], config_id: int, status: ReportSummaryStatus,
                 uri: Optional[str]) -> None:
        self.summary_id = summary_id
        self.config_id = config_id
        self.status = status
        self.uri = uri

    @staticmethod
    def _from_xml(xml: Element) -> 'ReportSummary':
        summary_id = xml.attrib.pop('id', None)
        config_id = xml.attrib.pop('cfg-id')
        status = ReportSummaryStatus(xml.attrib.pop('status'))
        uri = xml.attrib.pop('report-URI', None)

        return ReportSummary(summary_id=summary_id, config_id=config_id, status=status, uri=uri)


class ReportConfigSummary(XmlParse):
    """
    lies:
     - `name` exist
     - `date` can be empty string
    """

    def __init__(self, template_id: str, config_id: str, status: ReportSummaryStatus, generated_on: datetime.datetime,
                 report_uri: Optional[str], scope: Optional[ReportScope], name: Optional[str]) -> None:
        self.template_id = template_id
        self.config_id = config_id
        self.status = status
        self.generated_on = generated_on
        self.report_uri = report_uri
        self.scope = scope

        self.name = name

    @staticmethod
    def _from_xml(xml: Element) -> 'ReportConfigSummary':

        generated_on_raw = xml.attrib.pop('generated-on')
        if generated_on_raw == '':
            generated_on = None
        else:
            generated_on = datetime.datetime.strptime(generated_on_raw, '%Y%m%dT%H%M%S%f')

        return ReportConfigSummary(
            template_id=xml.attrib.pop('template-id'),
            config_id=xml.attrib.pop('cfg-id'),
            status=ReportSummaryStatus(xml.attrib.pop('status')),
            generated_on=generated_on,
            report_uri=xml.attrib.pop('report-URI', None),
            scope=XmlParse._pop(xml, 'scope', ReportScope),

            name=xml.attrib.pop('name', None),
        )
