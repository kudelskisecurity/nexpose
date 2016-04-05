import types

from lxml import etree
from lxml.etree import Element, SubElement
from typing import Iterable, Tuple, Optional

IP = Tuple[int, int, int, int]


class Object:
    def __repr__(self) -> str:
        """
        we also want to unfold the iterables as list
        """
        classname = self.__class__.__name__
        init = getattr(self, '__init__')

        args = init.__code__.co_varnames[1:]
        args_str = ['{{{}!r}}'.format(a) for a in args]

        ret = '{classname}({args})'.format(classname=classname, args=', '.join(args_str))
        values = dict()

        for k, v in self.__dict__.items():

            real_key = k
            if k not in args:
                real_key = next(arg for arg in args if arg.endswith(k))

            real_value = v
            if isinstance(v, types.GeneratorType):
                real_value = list(v)

            values[real_key] = real_value

        return ret.format(**values)


class XmlObject:
    def __init__(self, **kwargs) -> None:
        root = Element(self.__class__.__name__)
        root.attrib.update(kwargs)

        self.root = root

    def __bytes__(self) -> bytes:
        return etree.tostring(
            self.root,
            xml_declaration=True,
            pretty_print=True,
            encoding='UTF-8'
        )


class XmlCommunication:
    pass


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
