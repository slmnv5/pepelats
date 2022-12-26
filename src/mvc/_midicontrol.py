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
    pass
