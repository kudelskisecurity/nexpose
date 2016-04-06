from lxml.etree import Element

from nexpose.modules import ModuleBase
from nexpose.models.site import Site as SiteModel


class Site(ModuleBase):
    def save(self, site: SiteModel) -> str:
        request = Element('SiteSaveRequest')
        request.append(site.to_xml())

        ans = self._post(xml=request)

        return ans.get('site-id')

    def delete(self, site_id: str) -> None:
        request = Element('SiteDeleteRequest', attrib={
            'site-id': site_id,
        })

        self._post(xml=request)
