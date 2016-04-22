from typing import Iterable, Set

from nexpose.models import XmlParse
from nexpose.types import Element
from nexpose.utils import xml_pop_list, xml_text_pop


class Message(XmlParse['Message']):
    def __init__(self, message: str) -> None:
        self.message = message

    @staticmethod
    def _from_xml(xml: Element) -> 'Message':
        assert xml.tag == 'message'
        return Message(
            message=xml_text_pop(xml),
        )


class Stacktrace(XmlParse['Stacktrace']):
    @staticmethod
    def _from_xml(xml: Element):
        assert xml.tag == 'stacktrace'

        return Stacktrace()


class Exception(XmlParse['Exception']):
    def __init__(self, messages: Set[Message], stacktraces: Set[Stacktrace]) -> None:
        self.messages = messages
        self.stacktraces = stacktraces

    @staticmethod
    def _from_xml(xml: Element) -> 'Exception':
        assert xml.tag == 'Exception'
        return Exception(
            messages={Message.from_xml(x) for x in xml_pop_list(xml, 'message')},
            stacktraces={Stacktrace.from_xml(stack) for stack in xml_pop_list(xml, 'stacktrace')},
        )


class Failure(XmlParse['Failure']):
    def __init__(self, messages: Iterable[Message], exceptions: Iterable[Exception]) -> None:
        self.messages = messages
        self.exceptions = exceptions

    @staticmethod
    def _from_xml(xml: Element) -> 'Failure':
        assert xml.tag == 'Failure'

        messages = xml_pop_list(xml, 'Message') or xml_pop_list(xml, 'message')
        exceptions = xml_pop_list(xml, 'Exception')

        return Failure(
            messages={Message.from_xml(x) for x in messages},
            exceptions={Exception.from_xml(x) for x in exceptions},
        )
