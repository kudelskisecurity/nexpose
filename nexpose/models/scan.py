from typing import Iterable

from nexpose.models import XmlFormat, Object, XmlParse
from nexpose.types import Element


class Template(Object):
    def __init__(self, template_id: str) -> None:
        super().__init__()
        self.id = template_id


class ScanConfig(XmlFormat):
    def __init__(self, template: Template) -> None:
        super().__init__()
        self.template = template

    def _to_xml(self, root: Element) -> None:
        super()._to_xml(root)
        root.attrib['templateID'] = self.template.id


class Scan(Object):
    def __init__(self, scan_id: int) -> None:
        self.id = scan_id


class Vulnerabilities(XmlParse['Vulnerabilities']):

    @staticmethod
    def _from_xml(xml: Element) -> 'Vulnerabilities':
        pass


class ScanSummary(XmlParse['ScanSummary']):

    def __init__(self, vulnerabilities: Iterable[Vulnerabilities]) -> None:
        self.vulnerabilities = vulnerabilities

    @staticmethod
    def _from_xml(xml: Element) -> 'ScanSummary':
        pass
