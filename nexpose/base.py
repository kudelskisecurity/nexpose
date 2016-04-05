import logging

import requests
from lxml import etree
from lxml.etree import Element
from typing import Optional, Mapping, Tuple, Any

from nexpose.models.failure import Failure
from nexpose.networkerror import NetworkError

_Element = Any  # unable to retrieve real type from lxml


class NexposeBase:
    def __init__(self, host: str, port: int = 3780,
                 sessions_id: Optional[Mapping[Tuple[int, int], str]] = None) -> None:
        self.host = host
        self.port = port
        self.sessions_id = sessions_id or {
            (1, 1): None,
            (1, 2): None,
        }

        logging.captureWarnings(True)

    def _post(self, xml: _Element, api_version: Tuple[int, int] = (1, 1)) -> _Element:
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

    def __get_session(self):
        if '__session' not in self.__dict__:
            self.__session = None

        if not self.__session:
            session = requests.Session()
            session.headers['Content-Type'] = 'text/xml'
            self.__session = session
        else:
            self.__session.cookies.clear()  # nexpose dislike having login cookies and login for other thing

        return self.__session

    @staticmethod
    def __check_failure(xml: _Element, api_version: Tuple[int, int]) -> None:
        if api_version == (1, 1):
            if xml.attrib.get('success', None) == '1':
                return
            xml = xml[0]

        if api_version == (1, 2) and xml.tag != 'Failure':
            return

        failure = Failure.from_xml(xml=xml)
        raise NetworkError(failure=failure)
