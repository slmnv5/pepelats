import unittest
from unittest import TestCase

# noinspection PyProtectedMember
from loop._oneloopctrl import OneLoopCtrl
from utils import MAX_32_INT


class TestOneLoopCtrl(TestCase):

    def test_1(self):
        control = OneLoopCtrl()
        self.assertEqual(control.get_stop_len(), MAX_32_INT)
        self.assertFalse(control.is_stop_len_set())
        self.assertFalse(control.get_stop_event().is_set())


if __name__ == "__main__":
    unittest.main()
