import unittest

from lxml import etree

from nexpose.models.report import Paragraph


class TestReportRendering(unittest.TestCase):
    def test_paragraph_from_xml(self):
        elem = Paragraph.from_xml(etree.fromstring(
            """
            <Paragraph>
                <Paragraph>
                    javax.net.ssl.SSLException: Unrecognized SSL message, plaintext connection?
                </Paragraph>
            </Paragraph>
            """
        ))
        self.assertEqual(str(elem), 'javax.net.ssl.SSLException: Unrecognized SSL message, plaintext connection?')

    def test_description_from_xml(self):
        elem = Paragraph.from_xml(etree.fromstring(
            """
            <description>
                <ContainerBlockElement>
                    <Paragraph>
                        sapi/cgi/cgi_main.c in the CGI component in PHP through 5.4.36
                    </Paragraph>
                </ContainerBlockElement>
            </description>

            """
        ))
        self.assertEqual(str(elem), 'sapi/cgi/cgi_main.c in the CGI component in PHP through 5.4.36')
