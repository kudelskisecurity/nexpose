import uuid

from lxml.etree import SubElement
from typing import Iterable, Tuple, Optional

from nexpose.models import XmlFormat
from nexpose.models.scan import ScanConfig
from nexpose.types import IP, Element


class Hosts(XmlFormat):
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

        for ip_range_elem in self.ip_range:
            attribs = {
                'from': Hosts.__ip_to_str(ip=ip_range_elem[0]),
                'to': Hosts.__ip_to_str(ip=ip_range_elem[1]),
            }
            SubElement(root, 'host', attrib={k: v for k, v in attribs.items() if v is not None})


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
