import datetime
from enum import Enum
from uuid import uuid4

from lxml.etree import SubElement
from typing import Optional, Set

from nexpose.models import XmlParse, XmlFormat
from nexpose.models.scan import Scan
from nexpose.models.site import Site
from nexpose.types import Element, IP, str_to_IP
from nexpose.utils import xml_pop


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
        return ReportTemplateSummary(
            template_id=xml.attrib.pop('id'),
            name=xml.attrib.pop('name'),
            builtin=bool(xml.attrib.pop('builtin')),
            scope=ReportScope(xml.attrib.pop('scope')),
            template_type=ReportTemplateSummaryType(xml.attrib.pop('type')),
        )


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
    def __init__(self, template: ReportTemplateSummary, report_format: ReportConfigFormat, site: Site,
                 report_id: int = -1,
                 name: Optional[str] = None) -> None:
        if name is None:
            name = str(uuid4())

        self.template = template
        self.format = report_format
        self.site = site
        self.id = report_id
        self.name = name

    def _to_xml(self, root: Element) -> None:
        root.attrib.update({
            'id': str(self.id),
            'name': self.name,
            'template-id': self.template.id,
            'format': self.format.value,
        })

        filters = SubElement(root, 'Filters')
        SubElement(filters, 'filter', attrib={
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


class ReportSummary(XmlParse['ReportSummary']):
    def __init__(self, summary_id: Optional[int], config_id: int, status: ReportSummaryStatus,
                 uri: Optional[str]) -> None:
        self.summary_id = summary_id
        self.config_id = config_id
        self.status = status
        self.uri = uri

    @staticmethod
    def _from_xml(xml: Element) -> 'ReportSummary':
        return ReportSummary(
            summary_id=xml.attrib.pop('id', None),
            config_id=xml.attrib.pop('cfg-id'),
            status=ReportSummaryStatus(xml.attrib.pop('status')),
            uri=xml.attrib.pop('report-URI', None),
        )


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


class Fingerprint(XmlParse['Fingerprint']):
    """
    certainty="0.90" family="vsFTPd" product="vsFTPd" version="2.3.4"
    """

    def __init__(self, product: str, certainty: float, family: Optional[str], version: Optional[str],
                 vendor: Optional[str]) -> None:
        self.product = product
        self.certainty = certainty
        self.family = family
        self.version = version
        self.vendor = vendor

    @staticmethod
    def _from_xml(xml: Element) -> 'Fingerprint':
        fingerprint = Fingerprint(
            product=xml.attrib.pop('product', None),
            certainty=float(xml.attrib.pop('certainty')),
            family=xml.attrib.pop('family', None),
            version=xml.attrib.pop('version', None),
            vendor=xml.attrib.pop('vendor', None),
        )

        childs = {
            'os': OS.from_sub_xml,
            'fingerprint': Fingerprint.from_sub_xml,
        }

        return childs[xml.tag](fingerprint, xml)

    @staticmethod
    def from_sub_xml(fingerprint: 'Fingerprint', xml: Element) -> 'Fingerprint':
        return fingerprint


class DeviceClass(Enum):
    general = 'General'


class OS(Fingerprint):
    def __init__(self, product: str, certainty: float, family: Optional[str], version: Optional[str],
                 device_class: Optional[DeviceClass], vendor: Optional[str]) -> None:
        super().__init__(product=product, certainty=certainty, family=family, version=version, vendor=vendor)
        self.device_class = device_class

    @staticmethod
    def from_sub_xml(fingerprint: Fingerprint, xml: Element) -> 'OS':
        return OS(
            product=fingerprint.product,
            certainty=fingerprint.certainty,
            family=fingerprint.family,
            version=fingerprint.version,
            device_class=XmlParse._pop(xml, 'device-class', DeviceClass),
            vendor=fingerprint.vendor,
        )


class Name(XmlParse['Name']):
    def __init__(self, text: str) -> None:
        self.text = text

    @staticmethod
    def _from_xml(xml: Element) -> 'Name':
        return Name(
            text=xml.text,
        )


class PortStatus(Enum):
    open = 'open'


class Protocol(Enum):
    tcp = 'tcp'


class Config(XmlParse['Config']):
    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.text = text

    @staticmethod
    def _from_xml(xml: Element) -> 'Config':
        return Config(
            name=xml.attrib.pop('name'),
            text=xml.text,
        )


class Test(XmlParse['Test']):
    @staticmethod
    def _from_xml(xml: Element):
        return Test()


class Service(XmlParse):
    def __init__(self, name: str, fingerprints: Set[Fingerprint], configuration: Set[Config],
                 tests: Set[Test]) -> None:
        self.name = name
        self.fingerprints = fingerprints
        self.configuration = configuration
        self.tests = tests

    @staticmethod
    def _from_xml(xml: Element):
        return Service(
            name=xml.attrib.pop('name'),
            fingerprints={Fingerprint.from_xml(fingerprint) for fingerprint in xml_pop(xml, 'fingerprints', [])},
            configuration={Config.from_xml(config) for config in xml_pop(xml, 'configuration', [])},
            tests={Test.from_xml(test) for test in xml.find('tests')},
        )


class Endpoint(XmlParse['Endpoint']):
    def __init__(self, protocol: Protocol, port: int, status: PortStatus, services: Set[Service]) -> None:
        self.protocol = protocol
        self.port = port
        self.status = status
        self.services = services

    @staticmethod
    def _from_xml(xml: Element) -> 'Endpoint':
        return Endpoint(
            protocol=Protocol(xml.attrib.pop('protocol')),
            port=int(xml.attrib.pop('port')),
            status=PortStatus(xml.attrib.pop('status')),
            services={Service.from_xml(service) for service in xml.find('services')},
        )


class NodeStatus(Enum):
    alive = 'alive'


class SiteImportance(Enum):
    normal = 'Normal'


class Node(XmlParse['Node']):
    def __init__(self, address: IP, status: NodeStatus, device_id: int, site_name: str,
                 site_importance: SiteImportance,
                 scan_template_name: str, risk_score: float, names: Set[Name], fingerprints: Set[Fingerprint],
                 endpoints: Set[Endpoint]) -> None:
        self.address = address
        self.status = status
        self.device_id = device_id
        self.site_name = site_name
        self.site_importance = site_importance
        self.scan_template_name = scan_template_name
        self.risk_score = risk_score
        self.names = names
        self.fingerprints = fingerprints
        self.endpoints = endpoints

    @staticmethod
    def _from_xml(xml: Element) -> 'Node':
        return Node(
            address=str_to_IP(xml.attrib.pop('address')),
            status=NodeStatus(xml.attrib.pop('status')),
            device_id=xml.attrib.pop('device-id'),
            site_name=xml.attrib.pop('site-name'),
            site_importance=SiteImportance(xml.attrib.pop('site-importance')),
            scan_template_name=xml.attrib.pop('scan-template'),
            risk_score=float(xml.attrib.pop('risk-score')),
            names={Name.from_xml(name) for name in xml_pop(xml, 'names', [])},
            fingerprints={Fingerprint.from_xml(fingerprint) for fingerprint in xml.find('fingerprints')},
            endpoints={Endpoint.from_xml(endpoint) for endpoint in xml.find('endpoints')},
        )


class NexposeReport(XmlParse['NexposeReport']):
    def __init__(self, version: float, scans: Set[Scan], nodes: Set[Node]) -> None:
        self.version = version
        self.scans = scans
        self.nodes = nodes

    @staticmethod
    def _from_xml(xml: Element) -> 'NexposeReport':
        return NexposeReport(
            version=float(xml.attrib.pop('version')),
            scans={Scan.from_xml(scan) for scan in xml_pop(xml, 'scans')},
            nodes={Node.from_xml(node) for node in xml_pop(xml, 'nodes')},
        )
