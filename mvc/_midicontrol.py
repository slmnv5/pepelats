import logging
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from multiprocessing.dummy.connection import Pipe

from utils import CmdTranslator
from utils._utilalsa import MockMidiPort


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
