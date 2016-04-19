import uuid

from lxml.etree import SubElement
from typing import Iterable, Tuple, Optional

from nexpose.models import XmlFormat
from nexpose.models.scan import ScanConfig
from nexpose.types import IP, Element


class Hosts(XmlFormat):
    """
    lies:
     - we are not supposed to give ip_range as DNS host, but it works and the range doesn't
    """
    def __init__(self, ip_range: Iterable[Tuple[IP, Optional[IP]]], hosts: Iterable[str]) -> None:
        self.ip_range = ip_range
        self.hosts = hosts

    @staticmethod
    def __ip_to_str(ip: IP) -> Optional[str]:
        if ip is None:
            return None
        return '.'.join(str(i) for i in ip)

    def _to_xml(self, root: Element) -> None:
        super()._to_xml(root)

        for host in self.hosts:
            elem = SubElement(root, 'host')
            elem.text = host

        for ip in self.ip_range:
            elem = SubElement(root, 'host')
            elem.text = self.__ip_to_str(ip[0])


class Site(XmlFormat):
    """
    lies:
     - `id` has to be a number
    """

    def __init__(self, hosts: Hosts, scan_config: ScanConfig, name: Optional[str] = None, site_id: int = -1) -> None:
        if name is None:
            name = str(uuid.uuid4())
        self.id = site_id
        self.name = name
        self.hosts = hosts
        self.scan_config = scan_config

    def _to_xml(self, root: Element) -> None:
        super()._to_xml(root)

        root.attrib.update(dict(
            id=str(self.id),
            name=self.name,
        ))

        root.append(self.hosts.to_xml())
        SubElement(root, 'Credentials')
        SubElement(root, 'Alerting')
        root.append(self.scan_config.to_xml())
        SubElement(root, 'Tags')
