from nexpose.types import Element


class WeirdXMLError(Exception):
    pass


class NotFullyParsedError(WeirdXMLError):
    def __init__(self, element: Element) -> None:
        super().__init__(element, element.attrib, element.text, element.tail)


class AttribNotFullyParsedError(NotFullyParsedError):
    pass


class SubElementNotFullyParsedError(NotFullyParsedError):
    pass


class TextNotFullyParsedError(NotFullyParsedError):
    pass
