import logging
from functools import lru_cache

import requests
from lxml import etree
from lxml.etree import Element
from typing import Optional, Tuple, Mapping

from nexpose.models import Hosts, Site, ScanConfig
from nexpose.models.failure import Failure


class NexposeError(Exception):
    def __init__(self, failure: Failure):
        super().__init__(repr(failure))
        self.failure = failure


class Nexpose:
    def __init__(self, host: str, port: int = 3780,
                 sessions_id: Optional[Mapping[Tuple[int, int], str]] = None) -> None:
        self.host = host
        self.port = port
        self.sessions_id = sessions_id or {
            (1, 1): None,
            (1, 2): None,
        }

        logging.captureWarnings(True)

    def login(self, user_id: str, password: str, api_version: Tuple[int, int] = (1, 1)) -> str:
        request = Element('LoginRequest', attrib={
            'user-id': user_id,
            'password': password,
        })

        ans = self._post(xml=request, api_version=api_version)

        return ans.attrib['session-id']

    def logout(self, api_version: Tuple[int, int] = (1, 1)) -> None:
        request = Element('LogoutRequest')

        self._post(xml=request, api_version=api_version)

    def site_save(self, site: Site):
        request = Element('SiteSaveRequest')
        request.append(site.root)

        ans = self._post(xml=request)

        return None

    def _post(self, xml: Element, api_version: Tuple[int, int] = (1, 1)) -> Element:
        url = 'https://{host}:{port}/api/{api_version}/xml'.format(
            host=self.host,
            port=self.port,
            api_version='.'.join([str(v) for v in api_version])
        )

        session_id = self.sessions_id[api_version]
        if session_id is not None:
            xml.attrib['session-id'] = session_id

        req_raw = etree.tostring(xml,
                                 xml_declaration=True,
                                 pretty_print=True,
                                 encoding='UTF-8')

        session = self.__get_session()

        ans = session.post(url=url, data=req_raw, verify=False)
        ans_xml = etree.fromstring(ans.content)

        self.__check_failure(xml=ans_xml, api_version=api_version)

        return ans_xml

    @staticmethod
    @lru_cache(maxsize=1)
    def __get_session():
        session = requests.Session()
        session.headers['Content-Type'] = 'text/xml'

        return session

    @staticmethod
    def __check_failure(xml: Element, api_version: Tuple[int, int]) -> None:
        if api_version == (1, 1):
            if xml.attrib.get('success', None) == '1':
                return
            xml = xml[0]

        if api_version == (1, 2) and xml.tag != 'Failure':
            return

        failure = Failure.from_xml(xml=xml)
        raise NexposeError(failure=failure)
