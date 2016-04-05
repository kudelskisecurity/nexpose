import os
import unittest

from typing import Mapping, Optional, Any

from nexpose import Nexpose


# TODO but is simply matter of `first_false(lambda x: x is None, mapping)`
def __dict_full_none(mapping: Mapping[str, Optional[Any]]) -> bool:
    for v in mapping.values():
        if v is not None:
            return False
    return True


def _get_env_args() -> Mapping[str, str]:
    kwargs = {
        'host': os.environ['NEXPOSE_HOST'],
        'port': os.environ.get('NEXPOSE_PORT', None),
        'sessions_id': {
            (1, 1): os.environ.get('NEXPOSE_API_1_1_SESSION_ID', None),
            (1, 2): os.environ.get('NEXPOSE_API_1_2_SESSION_ID', None),
        }
    }

    return {k: v for k, v in kwargs.items()
            if v is not None and not (isinstance(v, dict) and __dict_full_none(v))}


class TestBase(unittest.TestCase):
    def setUp(self):
        self.nexpose = Nexpose(**_get_env_args())


class TestBaseLogged(TestBase):
    def setUp(self):
        super().setUp()

        sessions_id = {
            k: self.nexpose.login(
                user_id=os.environ['NEXPOSE_USER'],
                password=os.environ['NEXPOSE_PASS'],
                api_version=k,
            ) for k in [(1, 1), (1, 2)]}
        kwargs = dict(**_get_env_args())
        kwargs['sessions_id'] = sessions_id

        self.nexpose = Nexpose(**kwargs)

    def tearDown(self):
        super().tearDown()
        for api_version in [(1, 1), (1, 2)]:
            self.nexpose.logout(api_version=api_version)
