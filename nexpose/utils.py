from typing import Iterable

from nexpose.types import Element as ElementType


def xml_pop(xml: ElementType, key: str) -> ElementType:
    elem = xml.find(key)
    if elem is None:
        raise KeyError(key)

    xml.remove(elem)

    return elem


def xml_pop_list(xml: ElementType, key: str) -> Iterable[ElementType]:
    elems = xml.findall(key)

    for elem in elems:
        xml.remove(elem)

    return elems

