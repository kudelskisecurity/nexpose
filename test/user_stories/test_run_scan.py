from nexpose.models.site import Site
from nexpose.models.scan import ScanConfig
from test import TestBaseLogged


class TestRunScan(TestBaseLogged):
    def test_run_scan(self):

        template = next(t for t in self.nexpose.scan.templates() if t.id == 'discovery')

        site = Site(
            name='local network',
            hosts=self.hosts,
            scan_config=ScanConfig(template=template)
        )

        site_id = self.nexpose.site.save(site=site)
        self.nexpose.site.delete(site_id=site_id)
