from nexpose.models import XmlFormat, Object
from nexpose.types import Element


class Template(Object):
    def __init__(self, template_id: str) -> None:
        super().__init__()
        self.id = template_id


class ScanConfig(XmlFormat):
    def __init__(self, template: Template) -> None:
        super().__init__()
        self.template = template

    def _to_xml(self, root: Element) -> None:
        super()._to_xml(root)
        root.attrib['templateID'] = self.template.id
