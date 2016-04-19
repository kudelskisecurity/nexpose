import datetime
from enum import Enum

from typing import Iterable

from nexpose.models import XmlFormat, Object, XmlParse
from nexpose.types import Element


class Status(Enum):
    """
    lies:
     - `integrating` is not in DTD
    """
    running = 'running'
    finished = 'finished'
    stopped = 'stopped'
    error = 'error'
    dispatched = 'dispatched'
    paused = 'paused'
    aborted = 'aborted'
    unknown = 'unknown'

    integrating = 'integrating'


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


class Scan(XmlParse['Scan']):
    def __init__(self, scan_id: int, name: str, status: Status, start_time: datetime.datetime,
                 end_time: datetime.datetime) -> None:
        self.id = scan_id
        self.name = name
        self.status = status
        self.start_time = start_time
        self.end_time = end_time

    @staticmethod
    def _from_xml(xml: Element) -> 'Scan':
        scan_id = int(xml.attrib.pop('id'))
        name = xml.attrib.pop('name')
        status = Status(xml.attrib.pop('status'))
        start_time = datetime.datetime.strptime(xml.attrib.pop('startTime'), '%Y%m%dT%H%M%S%f')
        end_time = datetime.datetime.strptime(xml.attrib.pop('endTime'), '%Y%m%dT%H%M%S%f')

        return Scan(scan_id=scan_id, name=name, status=status, start_time=start_time, end_time=end_time)


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
