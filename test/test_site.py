from nexpose.models.site import Hosts, Site
from nexpose.models.scan import ScanConfig, Template
from nexpose.networkerror import NetworkError
from test import TestBaseLogged


class TestSite(TestBaseLogged):
    def __get_template(self) -> Template:
        return next(t for t in self.nexpose.scan.templates() if t.id == 'discovery')

    def test_site_save_no_host(self):
        template = self.__get_template()

        hosts = Hosts(ip_range=[], hosts=[])
        scan_config = ScanConfig(template=template)
        site = Site(name='test name', hosts=hosts, scan_config=scan_config)

        site_id = self.nexpose.site.site_save(site=site)
        self.nexpose.site.site_delete(site_id)

    def test_site_save(self):
        template = self.__get_template()

        hosts = Hosts(ip_range=[
            ((10, 0, 0, 1), None),
            ((10, 0, 0, 2), (10, 0, 0, 3)),
        ], hosts=[
            'server1.example.com',
            'server2.example.com',
            'server3.example.com',
            'server4.example.com',
            'server5.example.com',
        ])
        scan_config = ScanConfig(template=template)
        site = Site(name='test name', hosts=hosts, scan_config=scan_config)

        site_id = self.nexpose.site.site_save(site=site)
        self.nexpose.site.site_delete(site_id)



