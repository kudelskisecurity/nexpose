# Stubs for lxml.etree (Python 3.4)

from typing import Any, Dict, List, Tuple, Union, Generic, TypeVar, Iterable, MutableMapping, SupportsBytes, IO, \
    Optional

K = TypeVar('K')
V = TypeVar('V')


class _Attrib(Generic[K, V]):
    #     def __init__(self, *args, **kwargs): ...

    def __setitem__(self, key: K, value: V) -> None: ...

    def __delitem__(self, key: K) -> None: ...

    def update(self, sequence_or_dict: Union[Dict[K, V], '_Attrib[K, V]', Iterable[Tuple[K, V]]]) -> None: ...

    def pop(self, key: K, default: V) -> V: ...

    def clear(self) -> None: ...

    def __copy__(self) -> MutableMapping[K, V]: ...

    def __deepcopy__(self) -> MutableMapping[K, V]: ...

    def __getitem__(self, index: K) -> V: ...

    def __bool__(self) -> bool: ...

    def __len__(self) -> int: ...

    def get(self, key: K, default: V = ...) -> V: ...

    def keys(self) -> List[K]: ...

    def __iter__(self) -> Iterable[K]: ...

    def iterkeys(self) -> Iterable[K]: ...

    def values(self) -> List[V]: ...

    def itervalues(self) -> Iterable[V]: ...

    def items(self) -> List[Tuple[K, V]]: ...

    def iteritems(self) -> Iterable[Tuple[K, V]]: ...

    def has_key(self, key: K) -> bool: ...

    def __contains__(self, key: K) -> bool: ...

    def __eq__(self, other: Any) -> bool: ...

    def __ge__(self, other: Any) -> bool: ...

    def __gt__(self, other: Any) -> bool: ...

    def __le__(self, other: Any) -> bool: ...

    def __lt__(self, other: Any) -> bool: ...

    def __ne__(self, other: Any) -> bool: ...


class _Element:
    attrib = ...  # type: MutableMapping[str, _Attrib]
    tag = ...  # type: str
    text = ...  # type: str

    def append(self, element: '_Element') -> None: ...


AnyStr = Union[str, bytes]
ListAnyStr = Union[List[str], List[bytes]]
DictAnyStr = Union[Dict[str, str], Dict[bytes, bytes]]
Dict_Tuple2AnyStr_Any = Union[Dict[Tuple[str, str], Any], Tuple[bytes, bytes], Any]


# TODO maybe put it in lxml.parser
class _BaseParser:
    pass


class _ElementTree:
    def write(self,
              file: Union[AnyStr, IO],
              encoding: AnyStr = ...,
              method: AnyStr = ...,
              pretty_print: bool = ...,
              xml_declaration: Any = ...,
              with_tail: Any = ...,
              standalone: bool = ...,
              compression: int = ...,
              exclusive: bool = ...,
              with_comments: bool = ...,
              inclusive_ns_prefixes: ListAnyStr = ...) -> None:
        pass


def tostring(element_or_tree: Union[_Element, _ElementTree], *, encoding: Optional[str] = ..., method: str = ...,
             xml_declaration: Optional[bool] = ..., pretty_print: bool = ..., with_tail: bool = ...,
             standalone: Optional[int] = ..., doctype: Optional[str] = ..., exclusive: bool = ...,
             with_comments: bool = ..., inclusive_ns_prefixes: ListAnyStr = ...) -> Optional[bytes]: ...


def fromstring(text: AnyStr, parser: Optional[_BaseParser] = ..., *, base_url: Optional[AnyStr] = ...) -> _Element: ...


class _XSLTResultTree(SupportsBytes):
    pass


class _XSLTQuotedStringParam:
    pass


class XMLParser:
    pass


class XMLSchema:
    def __init__(self,
                 etree: Union[_Element, _ElementTree] = ...,
                 file: Union[AnyStr, IO] = ...) -> None:
        pass

    def assertValid(self,
                    etree: Union[_Element, _ElementTree]) -> None:
        pass


class XSLTAccessControl:
    pass


class XSLT:
    def __init__(self,
                 xslt_input: Union[_Element, _ElementTree],
                 extensions: Dict_Tuple2AnyStr_Any = ...,
                 regexp: bool = ...,
                 access_control: XSLTAccessControl = ...) -> None:
        pass

    def __call__(self,
                 _input: Union[_Element, _ElementTree],
                 profile_run: bool = ...,
                 **kwargs: Union[AnyStr, _XSLTQuotedStringParam]) -> _XSLTResultTree:
        pass

    @staticmethod
    def strparam(s: AnyStr) -> _XSLTQuotedStringParam:
        pass


def Element(_tag: AnyStr,
            attrib: DictAnyStr = ...,
            nsmap: DictAnyStr = ...,
            **extra: AnyStr) -> _Element:
    pass


def SubElement(_parent: _Element, _tag: AnyStr,
               attrib: DictAnyStr = ...,
               nsmap: DictAnyStr = ...,
               **extra: AnyStr) -> _Element:
    pass


def ElementTree(element: _Element = ...,
                file: Union[AnyStr, IO] = ...,
                parser: XMLParser = ...) -> _ElementTree:
    pass


def ProcessingInstruction(target: AnyStr, text: AnyStr = ...) -> _Element:
    pass


def parse(source: Union[AnyStr, IO],
          parser: XMLParser = ...,
          base_url: AnyStr = ...) -> _ElementTree:
    pass
