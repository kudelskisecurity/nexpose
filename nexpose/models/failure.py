from typing import Iterable, Optional

from nexpose.models import XmlParse
from nexpose.types import Element


class Message(XmlParse['Message']):
    def __init__(self, message: str) -> None:
        self.message = message

    @staticmethod
    def _from_xml(xml: Element) -> 'Message':
        return Message(
            message=xml.text,
        )


class Exception(XmlParse['Exception']):
    def __init__(self, message: str, stacktrace: Optional[str]) -> None:
        self.message = message
        self.stacktrace = stacktrace

    @staticmethod
    def _from_xml(xml: Element) -> 'Exception':
        message = xml[0].text
        stacktrace = None
        if len(xml) > 1:
            stacktrace = xml[1].text

        return Exception(
            message=message,
            stacktrace=stacktrace,
        )


class Failure(XmlParse['Failure']):
    def __init__(self, messages: Iterable[Message], exceptions: Iterable[Exception]) -> None:
        self.messages = messages
        self.exceptions = exceptions

    @staticmethod
    def _from_xml(xml: Element) -> 'Failure':
        return Failure(
            messages=(Message.from_xml(x) for x in xml.xpath('Message')),
            exceptions=(Exception.from_xml(x) for x in xml.xpath('Exception')),
        )
