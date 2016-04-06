import copy

from lxml.etree import Element

from nexpose.models.site import Site as SiteModel
from nexpose.modules import ModuleBase


class Site(ModuleBase):
    def save(self, site: SiteModel) -> SiteModel:
        request = Element('SiteSaveRequest')
        request.append(site.to_xml())

        ans = self._post(xml=request)

        site_id = ans.get('site-id')
        ret_site = copy.copy(site)
        ret_site.id = site_id

        return ret_site

    def delete(self, site: SiteModel) -> None:
        request = Element('SiteDeleteRequest', attrib={
            'site-id': site.id,
        })

        self._post(xml=request)
