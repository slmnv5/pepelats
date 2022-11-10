import time
import unittest
from multiprocessing.connection import Pipe
from unittest import TestCase

from drum import RDRUM
from loop import ExtendedCtrl

recv_conn, send_conn = Pipe(False)
ctrl = ExtendedCtrl(recv_conn, send_conn)
RDRUM.prepare_drum(2000)
time.sleep(1)


class TestExtendedCtrl(TestCase):

    def test_2(self):
        assert ctrl.item_count == 4
        line = ctrl._show_all_parts()
        print(line)


if __name__ == "__main__":
    unittest.main()
