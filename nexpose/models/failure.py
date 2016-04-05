from typing import Iterable, Optional

from nexpose.models import Object


class Message(Object):
    def __init__(self, message: str) -> None:
        self.message = message

    @staticmethod
    def from_xml(xml) -> 'Message':
        return Message(
            message=xml.text,
        )


class Exception(Object):
    def __init__(self, message: str, stacktrace: Optional[str]) -> None:
        self.message = message
        self.stacktrace = stacktrace

    @staticmethod
    def from_xml(xml) -> 'Exception':
        message = xml[0].text
        stacktrace = None
        if len(xml) > 1:
            stacktrace = xml[1].text

        return Exception(
            message=message,
            stacktrace=stacktrace,
        )


class Failure(Object):
    def __init__(self, messages: Iterable[Message], exceptions: Iterable[Exception]) -> None:
        self.messages = messages
        self.exceptions = exceptions

    @staticmethod
    def from_xml(xml) -> 'Failure':
        return Failure(
            messages=(Message.from_xml(x) for x in xml.xpath('Message')),
            exceptions=(Exception.from_xml(x) for x in xml.xpath('Exception')),
        )
