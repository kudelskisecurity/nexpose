from lxml.etree import SubElement
from typing import Iterable, Tuple, Optional

from nexpose.models import XmlObject, IP


class Hosts(XmlObject):
    def __init__(self, ip_range: Iterable[Tuple[IP, Optional[IP]]], hosts: Iterable[str]) -> None:
        super().__init__()

        for host in hosts:
            elem = SubElement(self.root, 'host')
            elem.text = host

        for ip_range_elem in ip_range:
            attribs = {
                'from': Hosts.__ip_to_str(ip=ip_range_elem[0]),
                'to': Hosts.__ip_to_str(ip=ip_range_elem[1]),
            }
            SubElement(self.root, 'host', attrib={k: v for k, v in attribs.items() if v is not None})

    @staticmethod
    def __ip_to_str(ip: IP) -> Optional[str]:
        if ip is None:
            return None
        return '.'.join(str(i) for i in ip)


class ScanConfig(XmlObject):
    def __init__(self, template_id: str) -> None:
        super().__init__(
            templateID=template_id,
        )


class Site(XmlObject):
    def __init__(self, site_id: int, name: str, hosts: Hosts, scan_config: ScanConfig) -> None:
        super().__init__(
            id=str(site_id),
            name=name,
        )
        self.root.append(hosts.root)
        SubElement(self.root, 'Credentials')
        SubElement(self.root, 'Alerting')
        self.root.append(scan_config.root)
        SubElement(self.root, 'Tags')