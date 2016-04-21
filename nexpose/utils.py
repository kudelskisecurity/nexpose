import datetime

from typing import Iterable, TypeVar, Callable

from nexpose.types import Element as ElementType

T = TypeVar('T')


def xml_pop_apply(xml: ElementType, key: str, func: Callable[[ElementType], ElementType],
                  *default: ElementType) -> ElementType:
    elem = xml.find(key)
    if elem is None:
        if len(default) == 0:
            raise KeyError(key)
        return default[0]

    xml.remove(elem)

    return func(elem)


def xml_pop(xml: ElementType, key: str, *default: ElementType) -> ElementType:
    return xml_pop_apply(xml, key, lambda x: x, *default)


def xml_pop_list(xml: ElementType, key: str) -> Iterable[ElementType]:
    elems = xml.findall(key)

    for elem in elems:
        xml.remove(elem)

    return elems


def xml_pop_children(xml: ElementType, key: str, *default: ElementType) -> Iterable[ElementType]:
    elem = xml_pop(xml, key, *default)
    children = list(elem)

    for child in children:
        elem.remove(child)

    return children


def parse_date(raw: str) -> datetime.datetime:
    return datetime.datetime.strptime(raw, '%Y%m%dT%H%M%S%f')
