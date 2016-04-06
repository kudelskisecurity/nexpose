from lxml.etree import Element
from typing import Tuple

from nexpose.modules import ModuleBase


class Session(ModuleBase):
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
