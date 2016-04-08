import time

from typing import Iterator

from nexpose.models.report import ReportConfig, ReportConfigFormat, ReportSummary, ReportConfigSummary, \
    ReportSummaryStatus
from nexpose.models.scan import ScanConfig
from nexpose.models.site import Site
from nexpose.modules.scan import ScanStatus
from test import TestBaseLogged


class TestRunScan(TestBaseLogged):
    def __get_report_from_listing(self, report: ReportSummary) -> Iterator[ReportConfigSummary]:
        return (r
                for r in self.nexpose.report.report_listing()
                if r.config_id == report.config_id)

    def __wait_until_report_completion(self, report: ReportSummary) -> None:
        while next(self.__get_report_from_listing(report)).status is not ReportSummaryStatus.generated:
            time.sleep(1)

    def test_run_scan(self):
        template = next(t for t in self.nexpose.scan.templates() if t.id == 'discovery')

        site = Site(
            hosts=self.hosts,
            scan_config=ScanConfig(template=template)
        )
        site_saved = self.nexpose.site.site_save(site=site)
        self.added_site.add(site_saved)

        scan = self.nexpose.scan.site_scan(site=site_saved)
        while self.nexpose.scan.scan_status(scan=scan) is not ScanStatus.finished:
            time.sleep(1)

        template = next(template
                        for template in self.nexpose.report.report_template_listing()
                        if template.id == 'audit-report')

        report = ReportConfig(template=template, format=ReportConfigFormat.raw_xml_v2, site=site_saved)
        report_saved = self.nexpose.report.report_save_request(report=report)

        report_summary = self.nexpose.report.report_generate(report=report_saved)
        self.__wait_until_report_completion(report=report_summary)
        reports_generated = self.__get_report_from_listing(report=report_summary)

        for report_generated in reports_generated:
            self.assertIsNotNone(report_generated.report_uri)
