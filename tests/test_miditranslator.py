import unittest
from multiprocessing import Pipe
from unittest import TestCase

# noinspection PyProtectedMember
from utils import CmdTranslator
from utils import ConfigName

recv_conn, send_conn = Pipe(False)
translator = CmdTranslator(send_conn, "config/midi", "playing", "0")


class TestMidiTranslator(TestCase):

    def test_1(self):
        translator._translate_and_send("60:100")

        msg = recv_conn.recv()
        if msg[0] == ConfigName.send_redraw:
            msg = recv_conn.recv()
        self.assertEqual(msg, ["_play_part_id", 0])
        self.assertFalse(recv_conn.poll())

    def test_2(self):
        translator._translate_and_send("60:6")
        msg = recv_conn.recv()
        if msg[0] == ConfigName.send_redraw:
            msg = recv_conn.recv()
        self.assertEqual(msg, ["_clear_part"])
        self.assertFalse(recv_conn.poll())


if __name__ == "__main__":
    unittest.main()
