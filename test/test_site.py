from nexpose.models.site import Hosts, ScanConfig, Site
from test import TestBaseLogged


class TestSite(TestBaseLogged):
    def test_site_save_no_host(self):
        hosts = Hosts(ip_range=[], hosts=[])
        scan_config = ScanConfig(template_id='full-audit')
        site = Site(site_id=-1, name='test name', hosts=hosts, scan_config=scan_config)

        site_id = self.nexpose.site.save(site=site)
        self.nexpose.site.delete(site_id)

    def test_site_save(self):
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
        scan_config = ScanConfig(template_id='full-audit')
        site = Site(site_id=-1, name='test name', hosts=hosts, scan_config=scan_config)

        site_id = self.nexpose.site.save(site=site)
        self.nexpose.site.delete(site_id)
