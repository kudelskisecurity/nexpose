from nexpose.networkerror import NetworkError
from test import TestBase


class TestLogin(TestBase):
    def test_correct_login(self):
        session_id = self.nexpose.session.login('nxadmin', 'nxadmin')
        self.assertRegex(session_id, '^[0-9A-F]{40}$')

    def test_wrong_login(self):
        self.assertRaises(NetworkError, self.nexpose.session.login, 'wrong username', 'wrong password')
