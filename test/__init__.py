import os
import unittest

from typing import Mapping, Optional, Any, Tuple
from typing import MutableSet

from nexpose import Nexpose
# TODO but is simply matter of `first_false(lambda x: x is None, mapping)`
from nexpose.models.site import Hosts
from nexpose.models.site import Site
from nexpose.types import IP


def __dict_full_none(mapping: Mapping[str, Optional[Any]]) -> bool:
    return any(x is not None for x in mapping.values())


def _get_env_args() -> Mapping[str, str]:
    kwargs = {
        'host': os.environ['NEXPOSE_HOST'],
        'port': os.environ.get('NEXPOSE_PORT', None),
        'sessions_id': None
    }

    return {k: v for k, v in kwargs.items()
            if v is not None and not (isinstance(v, dict) and __dict_full_none(v))}


class TestBase(unittest.TestCase):
    @staticmethod
    def __target_to_range(target: str) -> Tuple[IP, Optional[IP]]:
        target_splitted = target.split('.')

        if len(target_splitted) != 4:
            raise ValueError(target)

        return tuple(int(e) for e in target_splitted), None

    def setUp(self):
        self.nexpose = Nexpose(**_get_env_args())

        targets = os.environ['NEXPOSE_TARGETS'].split('|')
        self.hosts = Hosts(
            ip_range=(self.__target_to_range(ip) for ip in targets),
            hosts=[]
        )


class TestBaseLogged(TestBase):
    def setUp(self):
        super().setUp()

        sessions_id = {
            k: self.nexpose.session.login(
                user_id=os.environ['NEXPOSE_USER'],
                password=os.environ['NEXPOSE_PASS'],
                api_version=k,
            ) for k in [(1, 1)]}
        kwargs = dict(**_get_env_args())
        kwargs['sessions_id'] = sessions_id

        self.nexpose = Nexpose(**kwargs)

        self.added_site = set()  # type: MutableSet[Site]

    def tearDown(self):
        super().tearDown()

        for site in self.added_site:
            self.nexpose.site.site_delete(site=site)

        for api_version in [(1, 1)]:
            self.nexpose.session.logout(api_version=api_version)
