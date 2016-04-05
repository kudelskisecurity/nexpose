from nexpose import NexposeError
from test import TestBase


class TestLogin(TestBase):
    def test_correct_login(self):
        session_id = self.nexpose.login('nxadmin', 'nxadmin')
        self.assertRegex(session_id, '^[0-9A-F]{40}$')

    def test_wrong_login(self):
        self.assertRaises(NexposeError, self.nexpose.login, 'wrong username', 'wrong password')
