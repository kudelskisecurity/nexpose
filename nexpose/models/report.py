import abc
import datetime
from abc import abstractmethod
from enum import Enum
from uuid import uuid4

from lxml.etree import SubElement
from typing import Callable, Mapping, Optional, Set, Union, List, TypeVar, Generic

from nexpose.error import WeirdXMLError
from nexpose.models import XmlParse, XmlFormat
from nexpose.models.scan import Scan
from nexpose.models.site import Site
from nexpose.types import Element, IP, str_to_IP
from nexpose.utils import xml_pop, parse_date, xml_pop_children, xml_pop_list, xml_text_pop, xml_tail_pop

T = TypeVar('T')


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


class ReportTemplateSummary(XmlParse['ReportTemplateSummary']):
    def __init__(self, template_id: str, name: str, builtin: bool, scope: ReportScope,
                 template_type: ReportTemplateSummaryType, description: 'Description') -> None:
        self.id = template_id
        self.name = name
        self.builtin = builtin
        self.scope = scope
        self.template_type = template_type
        self.description = description

    @staticmethod
    def _from_xml(xml: Element) -> 'ReportTemplateSummary':
        assert xml.tag == 'ReportTemplateSummary'
        return ReportTemplateSummary(
            template_id=xml.attrib.pop('id'),
            name=xml.attrib.pop('name'),
            builtin=bool(xml.attrib.pop('builtin')),
            scope=ReportScope(xml.attrib.pop('scope')),
            template_type=ReportTemplateSummaryType(xml.attrib.pop('type')),
            description=Description.from_xml(xml_pop(xml, 'description')),
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


class ReportConfigSummary(XmlParse['ReportConfigSummary']):
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
            generated_on = parse_date(generated_on_raw)

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
        }  # type: Mapping[str, Callable[['Fingerprint', Element], 'Fingerprint']]

        return childs[xml.tag](fingerprint, xml)

    @staticmethod
    def from_sub_xml(fingerprint: 'Fingerprint', xml: Element) -> 'Fingerprint':
        return fingerprint


class DeviceClass(Enum):
    general = 'General'
    wap = 'WAP'
    storage = 'Storage'


class OS(Fingerprint):
    def __init__(self, product: str, certainty: float, family: Optional[str], version: Optional[str],
                 device_class: Optional[DeviceClass], vendor: Optional[str], arch: Optional[str]) -> None:
        super().__init__(product=product, certainty=certainty, family=family, version=version, vendor=vendor)
        self.device_class = device_class
        self.arch = arch

    @staticmethod
    def from_sub_xml(fingerprint: Fingerprint, xml: Element) -> 'OS':
        return OS(
            product=fingerprint.product,
            certainty=fingerprint.certainty,
            family=fingerprint.family,
            version=fingerprint.version,
            device_class=XmlParse._pop(xml, 'device-class', DeviceClass),
            vendor=fingerprint.vendor,
            arch=xml.attrib.pop('arch', None),
        )


class Name(XmlParse['Name']):
    def __init__(self, text: str) -> None:
        self.text = text

    @staticmethod
    def _from_xml(xml: Element) -> 'Name':
        return Name(
            text=xml_text_pop(xml),
        )


class PortStatus(Enum):
    open = 'open'


class Protocol(Enum):
    tcp = 'tcp'
    udp = 'udp'


class Config(XmlParse['Config']):
    def __init__(self, name: str, text: str) -> None:
        self.name = name
        self.text = text

    @staticmethod
    def _from_xml(xml: Element) -> 'Config':
        return Config(
            name=xml.attrib.pop('name'),
            text=xml_text_pop(xml),
        )


class TestStatus(Enum):
    not_vulnerable = 'not-vulnerable'
    overridden_vulnerable_version = 'overridden-vulnerable-version'
    skipped_version = 'skipped-version'
    vulnerable_version = 'vulnerable-version'
    vulnerable_exploited = 'vulnerable-exploited'
    skipped_disabled = 'skipped-disabled'
    error = 'error'
    unknown = 'unknown'


class PCIComplianceStatus(Enum):
    fail = 'fail'
    pass_ = 'pass'


NestedType = Union['Paragraph', 'UnorderedList', 'ContainerBlockElement', 'URLLink', 'OrderedList']


def dispatch_single_nested(xml: Element) -> NestedType:
    nested = {
        'Paragraph': Paragraph.from_xml,
        'UnorderedList': UnorderedList.from_xml,
        'ContainerBlockElement': ContainerBlockElement.from_xml,
        'URLLink': URLLink.from_xml,
        'OrderedList': OrderedList.from_xml,
        'Table': Table.from_xml,
    }

    return nested[xml.tag](xml)


def dispatch_nested_parsing(xml: Element) -> List[NestedType]:
    children = list(xml)
    for child in children:
        xml.remove(child)

    return [dispatch_single_nested(child) for child in children]


class TextElement(XmlParse[T], Generic[T], metaclass=abc.ABCMeta):
    @abstractmethod
    def __str__(self) -> str:
        pass


class MultiNestedElement(TextElement[T], Generic[T], metaclass=abc.ABCMeta):
    def __init__(self, nested: List[Union[str, NestedType]]) -> None:
        self.nested = nested

    @staticmethod
    def _parse_nested(xml: Element) -> List[Union[str, NestedType]]:
        ret = [xml_text_pop(xml), xml_tail_pop(xml)]  # type: List[Union[str, NestedType]]

        for child in xml:
            xml.remove(child)
            tail = xml_tail_pop(child)
            ret.append(dispatch_single_nested(child))
            ret.append(tail)

        return [r for r in ret if r is not None]

    def __str__(self) -> str:
        return ''.join(str(nested) for nested in self.nested)


class Description(MultiNestedElement['Description']):
    @staticmethod
    def _from_xml(xml: Element):
        assert xml.tag == 'description'

        return Description(
            nested=Description._parse_nested(xml),
        )


class URLLink(TextElement['URLLink']):
    def __init__(self, url: str, title: str, text: Optional[str]) -> None:
        self.url = url
        self.title = title
        self.text = text

    @staticmethod
    def _from_xml(xml: Element):
        if xml.attrib['LinkURL'] != xml.attrib.pop('href', xml.attrib['LinkURL']):
            raise WeirdXMLError('{} != {}', xml.attrib['LinkURL'], xml.attrib['href'])

        return URLLink(
            url=xml.attrib.pop('LinkURL'),
            title=xml.attrib.pop('LinkTitle'),
            text=xml_text_pop(xml),
        )

    def __str__(self) -> str:
        return '[{}]({})'.format(self.title, self.url)


class OrderedList(TextElement['OrderedList']):
    def __init__(self, elements: List[NestedType]) -> None:
        self.elements = elements

    @staticmethod
    def _from_xml(xml: Element):
        return OrderedList(
            elements=[ListItem.from_xml(item) for item in xml_pop_list(xml, 'ListItem')],
        )

    def __str__(self) -> str:
        return '\n'.join(' - {}'.format(element) for element in self.elements)


class ContainerBlockElement(MultiNestedElement['ContainerBlockElement']):
    def __init__(self, nested: List[NestedType], text: Optional[str]) -> None:
        super().__init__(nested=nested)
        self.text = text

    @staticmethod
    def _from_xml(xml: Element):
        return ContainerBlockElement(
            nested=dispatch_nested_parsing(xml),
            text=xml_text_pop(xml),
        )

    def __str__(self) -> str:
        return '\n'.join(str(nested) for nested in self.nested)


class TableCell(TextElement['TableCell']):
    def __init__(self, content: 'Paragraph') -> None:
        self.content = content

    @staticmethod
    def _from_xml(xml: Element):
        assert xml.tag == 'TableCell'
        return TableCell(
            content=Paragraph.from_xml(xml_pop(xml, 'Paragraph')),
        )

    def __str__(self) -> str:
        return '{}'.format(self.content)


class TableRow(TextElement['TableRow']):
    def __init__(self, title: str, cells: List[TableCell]) -> None:
        self.title = title
        self.cells = cells

    @staticmethod
    def _from_xml(xml: Element):
        assert xml.tag == 'TableRow'
        return TableRow(
            title=xml.attrib.pop('RowTitle'),
            cells=[TableCell.from_xml(cell) for cell in xml_pop_list(xml, 'TableCell')],
        )

    def __str__(self) -> str:
        return '{}\t{}'.format(self.title, '\t'.join(str(cell) for cell in self.cells))


class Table(TextElement['Table']):
    def __init__(self, title: str, rows: List[TableRow]) -> None:
        self.title = title
        self.rows = rows

    @staticmethod
    def _from_xml(xml: Element):
        assert xml.tag == 'Table'
        return Table(
            title=xml.attrib.pop('TableTitle'),
            rows=[TableRow.from_xml(row) for row in xml_pop_list(xml, 'TableRow')],
        )

    def __str__(self) -> str:
        return '{}\n{}'.format(self.title, '\n'.join(str(row) for row in self.rows))


class ListItem(MultiNestedElement['ListItem']):
    def __init__(self, text: str, nested: List[NestedType]) -> None:
        super().__init__(nested=nested)
        self.text = text

    @staticmethod
    def _from_xml(xml: Element):
        return ListItem(
            text=xml_text_pop(xml),
            nested=ListItem._parse_nested(xml),
        )

    def __str__(self) -> str:
        return '{}\n{}'.format(self.text, '\n'.join(str(nested) for nested in self.nested))


class UnorderedList(TextElement['UnorderedList']):
    def __init__(self, items: Set[ListItem]) -> None:
        self.items = frozenset(items)

    @staticmethod
    def _from_xml(xml: Element):
        return UnorderedList(
            items={ListItem.from_xml(item) for item in xml_pop_list(xml, 'ListItem')}
        )

    def __str__(self) -> str:
        return '\n'.join(' - {}'.format(item) for item in self.items)


class Paragraph(MultiNestedElement['Paragraph']):
    def __init__(self, nested: List[Union[str, NestedType]], preformat: Optional[bool]) -> None:
        super().__init__(nested=nested)
        self.preformat = preformat

    @staticmethod
    def _from_xml(xml: Element):
        nested = Paragraph._parse_nested(xml)

        preformat = xml.attrib.pop('preformat', None) or xml.attrib.pop('preFormat', None)
        if preformat is not None:
            preformat = bool(preformat)

        return Paragraph(
            nested=nested,
            preformat=preformat,
        )


class Test(XmlParse['Test']):
    def __init__(self, test_id: str, status: TestStatus, key: str, scan_id: int,
                 vulnerable_since: Optional[datetime.datetime],
                 pci_compliance_status: Optional[PCIComplianceStatus], paragraph: Paragraph) -> None:
        self.id = test_id
        self.status = status
        self.key = key
        self.scan_id = scan_id
        self.vulnerable_since = vulnerable_since
        self.pci_compliance_status = pci_compliance_status
        self.paragraph = paragraph

    @staticmethod
    def _from_xml(xml: Element):
        paragraph_xml = xml_pop(xml, 'Paragraph', None)
        if paragraph_xml is None:
            paragraph = None
        else:
            paragraph = Paragraph.from_xml(paragraph_xml)

        return Test(
            test_id=xml.attrib.pop('id'),
            status=TestStatus(xml.attrib.pop('status')),
            key=xml.attrib.pop('key'),
            scan_id=xml.attrib.pop('scan-id'),
            vulnerable_since=XmlParse._pop(xml, 'vulnerable-since', parse_date),
            pci_compliance_status=XmlParse._pop(xml, 'pci-compliance-status', PCIComplianceStatus),
            paragraph=paragraph,
        )


class Service(XmlParse['Service']):
    def __init__(self, name: str, fingerprints: Set[Fingerprint], configuration: Set[Config],
                 tests: Set[Test]) -> None:
        self.name = name
        self.fingerprints = frozenset(fingerprints)
        self.configuration = frozenset(configuration)
        self.tests = frozenset(tests)

    @staticmethod
    def _from_xml(xml: Element):
        return Service(
            name=xml.attrib.pop('name'),
            fingerprints={Fingerprint.from_xml(fingerprint) for fingerprint in
                          xml_pop_children(xml, 'fingerprints', [])},
            configuration={Config.from_xml(config) for config in xml_pop_children(xml, 'configuration', [])},
            tests={Test.from_xml(test) for test in xml_pop_children(xml, 'tests')},
        )


class Endpoint(XmlParse['Endpoint']):
    def __init__(self, protocol: Protocol, port: int, status: PortStatus, services: Set[Service]) -> None:
        self.protocol = protocol
        self.port = port
        self.status = status
        self.services = frozenset(services)

    @staticmethod
    def _from_xml(xml: Element) -> 'Endpoint':
        return Endpoint(
            protocol=Protocol(xml.attrib.pop('protocol')),
            port=int(xml.attrib.pop('port')),
            status=PortStatus(xml.attrib.pop('status')),
            services={Service.from_xml(service) for service in xml_pop_children(xml, 'services')},
        )


class NodeStatus(Enum):
    alive = 'alive'


class SiteImportance(Enum):
    normal = 'Normal'


class Node(XmlParse['Node']):
    def __init__(self, address: IP, status: NodeStatus, device_id: int, site_name: str,
                 site_importance: SiteImportance, scan_template_name: str, risk_score: float, names: Set[Name],
                 hardware_address: Optional[str], fingerprints: Set[Fingerprint], software: Set[Fingerprint],
                 endpoints: Set[Endpoint], tests: Set[Test]) -> None:
        self.address = address
        self.status = status
        self.device_id = device_id
        self.site_name = site_name
        self.site_importance = site_importance
        self.scan_template_name = scan_template_name
        self.risk_score = risk_score
        self.hardware_address = hardware_address
        self.names = frozenset(names)
        self.fingerprints = frozenset(fingerprints)
        self.software = frozenset(software)
        self.endpoints = frozenset(endpoints)
        self.tests = frozenset(tests)

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
            hardware_address=xml.attrib.pop('hardware-address', None),
            names={Name.from_xml(name) for name in xml_pop_children(xml, 'names', [])},
            fingerprints={Fingerprint.from_xml(fingerprint) for fingerprint in xml_pop_children(xml, 'fingerprints')},
            software={Fingerprint.from_xml(fingerprint) for fingerprint in xml_pop_children(xml, 'software', [])},
            endpoints={Endpoint.from_xml(endpoint) for endpoint in xml_pop_children(xml, 'endpoints')},
            tests={Test.from_xml(test) for test in xml_pop_children(xml, 'tests')},
        )


class Malware(XmlParse['Malware']):
    def __init__(self, name: Set[Name]) -> None:
        self.name = name

    @staticmethod
    def _from_xml(xml: Element):
        return Malware(
            name={Name.from_xml(name) for name in xml_pop_list(xml, 'name')},
        )


class ExploitType(Enum):
    exploitdb = 'exploitdb'
    metasploit = 'metasploit'


class SkillLevel(Enum):
    intermediate = 'Intermediate'
    expert = 'Expert'
    novice = 'Novice'


class Exploit(XmlParse['Exploit']):
    def __init__(self, exploit_id: int, title: str, exploit_type: ExploitType, link: str,
                 skill_level: SkillLevel) -> None:
        self.exploit_id = exploit_id
        self.title = title
        self.type = exploit_type
        self.link = link
        self.skill_level = skill_level

    @staticmethod
    def _from_xml(xml: Element):
        return Exploit(
            exploit_id=xml.attrib.pop('id'),
            title=xml.attrib.pop('title'),
            exploit_type=ExploitType(xml.attrib.pop('type')),
            link=xml.attrib.pop('link'),
            skill_level=SkillLevel(xml.attrib.pop('skillLevel')),
        )


class ReferenceSource(Enum):
    apple = 'APPLE'
    bid = 'BID'
    ciac = 'CIAC'
    conectiva = 'CONECTIVA'
    cve = 'CVE'
    redhat = 'REDHAT'
    sgi = 'SGI'
    url = 'URL'
    xf = 'XF'
    caldera = 'CALDERA'
    mandrake = 'MANDRAKE'
    debian = 'DEBIAN'
    cert = 'CERT'
    osvdb = 'OSVDB'
    suse = 'SUSE'
    oval = 'OVAL'
    disa_severity = 'DISA_SEVERITY'
    disa_vmskey = 'DISA_VMSKEY'
    iavm = 'IAVM'
    cert_vn = 'CERT-VN'
    ms = 'MS'
    netbsd = 'NETBSD'
    mskb = 'MSKB'
    mandriva = 'MANDRIVA'
    sectrack = 'SECTRACK'


class Reference(XmlParse['Reference']):
    def __init__(self, source: ReferenceSource, text: str) -> None:
        self.source = source
        self.text = text

    @staticmethod
    def _from_xml(xml: Element):
        return Reference(
            source=ReferenceSource(xml.attrib.pop('source')),
            text=xml_text_pop(xml),
        )


class Tag(XmlParse['Tag']):
    def __init__(self, text: str) -> None:
        self.text = text

    @staticmethod
    def _from_xml(xml: Element):
        return Tag(
            text=xml_text_pop(xml),
        )


class Solution(MultiNestedElement['Solution']):
    @staticmethod
    def _from_xml(xml: Element):
        assert xml.tag == 'solution'

        return Solution(
            nested=Solution._parse_nested(xml),
        )


class Vulnerability(XmlParse['Vulnerability']):
    def __init__(self, vulnerability_id: str, title: str, severity: int, pci_severity: int, cvss_score: float,
                 cvss_vector: str, published: datetime.datetime, added: datetime.datetime, modified: datetime.datetime,
                 risk_score: float, malware: Malware, exploits: Set[Exploit], description: ContainerBlockElement,
                 references: Set[Reference], tags: Set[Tag], solution: ContainerBlockElement) -> None:
        self.vulnerability_id = vulnerability_id
        self.title = title
        self.severity = severity
        self.pci_severity = pci_severity
        self.cvss_score = cvss_score
        self.cvss_vector = cvss_vector
        self.published = published
        self.added = added
        self.modified = modified
        self.risk_score = risk_score
        self.malware = malware
        self.exploits = exploits
        self.description = description
        self.references = references
        self.tags = tags
        self.solution = solution

    @staticmethod
    def _from_xml(xml: Element):
        assert xml.tag == 'vulnerability'
        return Vulnerability(
            vulnerability_id=xml.attrib.pop('id'),
            title=xml.attrib.pop('title'),
            severity=int(xml.attrib.pop('severity')),
            pci_severity=int(xml.attrib.pop('pciSeverity')),
            cvss_score=float(xml.attrib.pop('cvssScore')),
            cvss_vector=xml.attrib.pop('cvssVector'),
            published=parse_date(xml.attrib.pop('published')),
            added=parse_date(xml.attrib.pop('added')),
            modified=parse_date(xml.attrib.pop('modified')),
            risk_score=float(xml.attrib.pop('riskScore')),
            malware=Malware.from_xml(xml_pop(xml, 'malware')),
            exploits={Exploit.from_xml(exploit) for exploit in xml_pop_children(xml, 'exploits')},
            description=Description.from_xml(xml_pop(xml, 'description')),
            references={Reference.from_xml(reference) for reference in xml_pop_children(xml, 'references')},
            tags={Tag.from_xml(tag) for tag in xml_pop_children(xml, 'tags')},
            solution=Solution.from_xml(xml_pop(xml, 'solution')),
        )


class NexposeReport(XmlParse['NexposeReport']):
    def __init__(self, version: float, scans: Set[Scan], nodes: Set[Node],
                 vulnerability_definition: Set[Vulnerability]) -> None:
        self.version = version
        self.scans = frozenset(scans)
        self.nodes = frozenset(nodes)
        self.vulnerability_definition = vulnerability_definition

    @staticmethod
    def _from_xml(xml: Element) -> 'NexposeReport':
        return NexposeReport(
            version=float(xml.attrib.pop('version')),
            scans={Scan.from_xml(scan) for scan in xml_pop_children(xml, 'scans')},
            nodes={Node.from_xml(node) for node in xml_pop_children(xml, 'nodes')},
            vulnerability_definition={Vulnerability.from_xml(vulnerability) for vulnerability in
                                      xml_pop_children(xml, 'VulnerabilityDefinitions')},
        )
