import types

from lxml import etree
from lxml.etree import Element
from typing import Iterable, Tuple, Any, cast

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
                real_value = list(cast(Iterable[Any], v))

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
