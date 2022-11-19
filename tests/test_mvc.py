import unittest
from multiprocessing.dummy.connection import Pipe
from unittest import TestCase

from mvc import MidiControl
# noinspection PyProtectedMember
from utils._utilalsa import MockMidiPort

recv_loop, send_loop = Pipe()
recv_view, send_view = Pipe()


class TestMVC(TestCase):

    def test_1(self):

        in_port = MockMidiPort()
        in_port.charge({0.1: (60, 100), 0.2: (-60, 0), 1.2: (62, 1)})

        m_ctrl = MidiControl(in_port, send_loop, "config/midi", "playing", "0")
        try:
            m_ctrl.monitor()  # MockInMidiPort throws EOF when all mesages processed
        except EOFError:
            pass

        print("===================")
        while recv_loop.poll():
            msg = recv_loop.recv(timeout=0.001)
            print(msg)


if __name__ == "__main__":
    unittest.main()
