from typing import Iterable, TypeVar

from nexpose.types import Element as ElementType

T = TypeVar('T')


def xml_pop(xml: ElementType, key: str, *default: ElementType) -> ElementType:
    elem = xml.find(key)
    if elem is None:
        if len(default) == 0:
            raise KeyError(key)
        return default[0]

    xml.remove(elem)

    return elem


def xml_pop_list(xml: ElementType, key: str) -> Iterable[ElementType]:
    elems = xml.findall(key)

    for elem in elems:
        xml.remove(elem)

    return elems
