from lxml.etree import Element

from nexpose.models.site import Site as SiteModel
from nexpose.base import NexposeBase


class Site(NexposeBase):
    def save(self, site: SiteModel):
        request = Element('SiteSaveRequest')
        request.append(site.root)

        ans = self._post(xml=request)

        return None
