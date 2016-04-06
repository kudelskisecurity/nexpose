import time

from nexpose.models.scan import ScanConfig
from nexpose.models.site import Site
from nexpose.modules.scan import ScanStatus
from test import TestBaseLogged


class TestRunScan(TestBaseLogged):
    def test_run_scan(self):
        template = next(t for t in self.nexpose.scan.templates() if t.id == 'discovery')

        site = Site(
            name='local network',
            hosts=self.hosts,
            scan_config=ScanConfig(template=template)
        )

        site_saved = self.nexpose.site.site_save(site=site)

        scan = self.nexpose.scan.site_scan(site=site_saved)

        while self.nexpose.scan.scan_status(scan=scan) is not ScanStatus.finished:
            time.sleep(1)

        self.nexpose.site.site_delete(site=site_saved)
