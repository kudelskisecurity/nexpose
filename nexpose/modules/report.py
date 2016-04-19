import copy

from lxml.etree import Element
from typing import Iterable

from nexpose.models.report import ReportTemplateSummary, ReportConfig, ReportSummary, ReportConfigSummary
from nexpose.modules import ModuleBase
from nexpose.utils import xml_pop_list, xml_pop



class Report(ModuleBase):
    def report_template_listing(self) -> Iterable[ReportTemplateSummary]:
        request = Element('ReportTemplateListingRequest')

        ans = self._post(xml=request)

        templates = xml_pop_list(xml=ans, key='ReportTemplateSummary')

        return (ReportTemplateSummary.from_xml(template) for template in templates)

    def report_save_request(self, report: ReportConfig) -> ReportConfig:
        request = Element('ReportSaveRequest')
        request.append(report.to_xml())

        ans = self._post(xml=request)

        ret = copy.copy(report)
        ret.id = ans.attrib['reportcfg-id']

        return ret

    def report_generate(self, report: ReportConfig) -> ReportSummary:
        request = Element('ReportGenerateRequest', attrib={
            'report-id': str(report.id),
        })

        ans = self._post(xml=request)

        return ReportSummary.from_xml(xml_pop(xml=ans, key='ReportSummary'))

    def report_listing(self) -> Iterable[ReportConfigSummary]:
        request = Element('ReportListingRequest')

        ans = self._post(xml=request)

        return (ReportConfigSummary.from_xml(report) for report in xml_pop_list(xml=ans, key='ReportConfigSummary'))

