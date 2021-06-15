from unittest import mock
from email_handler.email_tool import Email_tool
import unittest
from unittest.mock import patch
import ssl

class TestEmail_tool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.my_emailer = Email_tool('sender@email.com', 'Password123')

    def tearDown(self):
        del self.my_emailer

    def test_init(self):
        self.assertEqual(self.my_emailer.port, 587)
        self.assertEqual(self.my_emailer.sender_email, 'sender@email.com')
        self.assertEqual(self.my_emailer.password, 'Password123')
        self.assertIsInstance(self.my_emailer.context, ssl.SSLContext)

if __name__ == '__main__':
    unittest.main()
