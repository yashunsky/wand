import _preamble

import unittest

from third_party.mock import patch, Mock
import wand_gui


class MockSerial():
    def read(self, val):
        return '8 9\r\n1 2 3 4 5 6 7 8 9\r\n12 15'

    def inWaiting(self):
        return None


class MockListener(wand_gui.Listener):
    def __init__(self, core_file_name):
        self.data_buffer = ''
        self.incoming_data = []
        self.serial = MockSerial()


class CheckListener(unittest.TestCase):
    @patch('wand_gui.time', return_value=11111.11)
    def test_get_data(self, mock_time):
        listener = MockListener('mock_file')
        listener.get_data()
        self.assertEqual(listener.data_buffer, '12 15')
        self.assertEqual(listener.incoming_data,
                         [[11111.11, 1., 2., 3., 4., 5., 6., 7., 8., 9.]])


if __name__ == '__main__':
    unittest.main()
