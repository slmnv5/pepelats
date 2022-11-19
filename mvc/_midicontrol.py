import logging
import time
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from multiprocessing.dummy.connection import Pipe
from typing import Dict, Tuple

import mido

from utils import CmdTranslator


class MockMidiPort:
    def __init__(self, report_freq: int = 100):
        self.__notes: Dict[float, mido.Message] = dict()
        self.__count: int = 0
        self.__report_freq: int = report_freq  # report sent messages: 100 - ervery 100th message

    def charge(self, notes: Dict[float, Tuple[int, int]]):
        """set dictionary of {time: (note,vel), ...} to send e.g. {0.1: (60,100), 0.2: (-60,0), 1.2:(62, 1)}
        negative values are note off messages"""
        self.__notes.clear()
        for k, v in notes.items():
            if v[0] >= 0 and v[1] > 0:
                self.__notes[k] = mido.Message.from_bytes([0x90, v[0], v[1]])
            else:
                self.__notes[k] = mido.Message.from_bytes([0x80, -v[0], 0])

    def send(self, msg: mido.Message) -> None:
        self.__count += 1
        if self.__count % self.__report_freq == 0:
            print(f"Sent MIDI {msg}")

    # noinspection PyUnusedLocal
    def receive(self, block=True) -> mido.Message:
        if len(self.__notes) == 0:
            raise EOFError

        k = list(self.__notes)[0]
        time.sleep(k)
        return self.__notes.pop(k)


class MidiControl(CmdTranslator):

    def __init__(self, in_port, send_conn: Connection, directory: str, map_name: str, map_id: str):
        CmdTranslator.__init__(self, send_conn, directory, map_name, map_id)
        self.__in_port = in_port

    def monitor(self) -> None:
        logging.info("Started MidiController")
        while True:
            msg = self.__in_port.receive(block=True)
            logging.debug(f"{self.__class__.__name__} got MIDI message: {msg}")

            note = msg.bytes()[1]
            vel = msg.bytes()[2]
            self._translate_and_send(f"{note}:{vel}")

    def __str__(self):
        return f"{self.__class__.__name__}"


if __name__ == "__main__":

    def test():
        recv_fake, send_fake = Pipe()
        in_port = MockMidiPort()
        in_port.charge({0.1: (60, 100), 0.2: (-60, 0), 1.2: (62, 1)})

        m_ctrl = MidiControl(in_port, send_fake, "config/midi", "playing", "0")
        try:
            m_ctrl.monitor()  # will throw EOF when all mesages processed
        except EOFError:
            pass

        send_fake.close()
        print("===================")
        while recv_fake.poll():
            msg = recv_fake.recv(timeout=0.001)
            print(msg)


    test()
