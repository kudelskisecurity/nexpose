from nexpose.models.report import ReportConfigSummary, NexposeReport
from nexpose.modules import ModuleBase


class Extra(ModuleBase):
    def get_report_raw_xml_2(self, report: ReportConfigSummary) -> NexposeReport:
        xml = self._get_xml(report.report_uri[1:])
        return NexposeReport.from_xml(xml)
