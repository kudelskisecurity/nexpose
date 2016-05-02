import time

from requests.exceptions import ConnectionError
from typing import Iterator

from nexpose.models.report import ReportConfig, ReportConfigFormat, ReportSummary, ReportConfigSummary, \
    ReportSummaryStatus
from nexpose.models.scan import ScanConfig, Status
from nexpose.models.site import Site
from test import TestBaseLogged


class TestRunScan(TestBaseLogged):
    def __get_report_from_listing(self, report: ReportSummary) -> Iterator[ReportConfigSummary]:
        return (r
                for r in self.nexpose.report.report_listing()
                if r.config_id == report.config_id)

    def __wait_until_report_completion(self, report: ReportSummary) -> None:
        while next(self.__get_report_from_listing(report)).status is not ReportSummaryStatus.generated:
            time.sleep(1)

    def __wait_until_scan_completion(self, scan_id: int) -> None:
        while True:
            try:
                if self.nexpose.scan.scan_status(scan_id=scan_id) is Status.finished:
                    return
            except ConnectionError:
                pass
            time.sleep(1)

    def test_run_scan_discovery(self):
        self.__run_scan('discovery')

    def test_run_scan_full_audit(self):
        self.__run_scan('full-audit')

    def test_run_scan_pentest_audit(self):
        self.__run_scan('pentest-audit')

    def __run_scan(self, scan_template_name: str):
        template = next(t for t in self.nexpose.scan.templates() if t.id == scan_template_name)

        site = Site(
            hosts=self.hosts,
            scan_config=ScanConfig(template=template)
        )
        site_saved = self.nexpose.site.site_save(site=site)
        self.added_site.add(site_saved)

        scan_id = self.nexpose.scan.site_scan(site=site_saved)
        self.__wait_until_scan_completion(scan_id)

        template = next(template
                        for template in self.nexpose.report.report_template_listing()
                        if template.id == 'audit-report')

        report = ReportConfig(template=template, report_format=ReportConfigFormat.raw_xml_v2, site=site_saved)
        report_saved = self.nexpose.report.report_save_request(report=report)

        report_summary = self.nexpose.report.report_generate(report=report_saved)
        self.__wait_until_report_completion(report=report_summary)
        report_generated = next(self.__get_report_from_listing(report=report_summary))

        self.assertIsNotNone(report_generated.report_uri)

        report_parsed = self.nexpose.extra.get_report_raw_xml_2(report_generated)
        self.assertIsNotNone(report_parsed)

        frozenset([report_parsed])  # ensure that everything is hashable
