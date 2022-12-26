import logging
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from mvc.menucontrol import MenuControl, MenuLoader


class MidiControl(MenuControl):

    def __init__(self, in_port, send_conn: Connection, menu_loader: MenuLoader):
        MenuControl.__init__(self, send_conn, menu_loader)
        self.__in_port = in_port

    def monitor(self) -> None:
        logging.info("Started MidiControl's monitor")
        while True:
            msg = self.__in_port.receive()
            logging.debug(f"{self.__class__.__name__} got MIDI message: {msg}")

            note = msg[1]
            velo = msg[2]
            self._send(f"{note}:{velo}")

    def __str__(self):
        return f"{self.__class__.__name__}"


if __name__ == "__main__":

    def test():
        from utils.utilport import ChargedMidiPort
        from multiprocessing.dummy.connection import Pipe
        recv_fake, send_fake = Pipe()
        in_port = ChargedMidiPort()
        in_port.charge({0.1: (60, 100), 0.2: (-60, 0), 1.2: (62, 1)})
        menu_loader = MenuLoader("config/menu", "play", "0")
        m_ctrl = MidiControl(in_port, send_fake, menu_loader)
        try:
            m_ctrl.monitor()  # will throw EOF when all mesages processed
        except EOFError:
            pass

        send_fake.close()
        while recv_fake.poll():
            msg = recv_fake.recv(timeout=0.001)
            logging.debug(msg)


    test()
