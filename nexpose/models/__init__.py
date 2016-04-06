import types
from abc import ABCMeta, abstractmethod

from lxml import etree
from typing import Iterable, Any, cast, TypeVar, Generic

from nexpose.types import Element


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
                real_value = list(cast(Iterable[Any], v))

            values[real_key] = real_value

        return ret.format(**values)


SubClass = TypeVar('SubClass')


class XmlParse(Object, Generic[SubClass], metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def _from_xml(xml: Element) -> SubClass:
        pass

    @classmethod
    def from_xml(cls, xml: Element) -> SubClass:
        ret = cls._from_xml(xml)  # type: SubClass

        # TODO check for xml emptyness

        return ret


class XmlFormat(Object, metaclass=ABCMeta):
    @abstractmethod
    def _to_xml(self, root: Element) -> None:
        pass

    def to_xml(self) -> Element:
        root = etree.Element(self.__class__.__name__)

        self._to_xml(root)

        return root

    def __bytes__(self) -> bytes:
        return etree.tostring(
            self.to_xml(),
            xml_declaration=True,
            pretty_print=True,
            encoding='UTF-8'
        )
