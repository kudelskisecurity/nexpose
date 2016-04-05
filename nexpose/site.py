from lxml.etree import Element

from nexpose.base import NexposeBase
from nexpose.models.site import Site as SiteModel


class Site(NexposeBase):
    def save(self, site: SiteModel) -> str:
        request = Element('SiteSaveRequest')
        request.append(site.root)

        ans = self._post(xml=request)

        return ans.get('site-id')

    def delete(self, site_id: str) -> None:
        request = Element('SiteDeleteRequest', attrib={
            'site-id': site_id,
        })

        self._post(xml=request)
