import logging
import os
import sys
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from mvc import CountMidiControl
from mvc import MidiControl
from mvc._pyscreen import PyScreen
from mvc.menucontrol import MenuLoader, MenuControl
from utils.utilconfig import ConfigName, ENV_ROOT_DIR, ENV_FRAME_BUFFER_ID, ENV_USE_TEXT


class ControlFactory:
    def __init__(self, in_port, recv_conn: Connection, send_conn: Connection, menu_loader: MenuLoader):
        self.in_port = in_port
        self.send_conn = send_conn
        self.recv_conn = recv_conn
        self.menu_loader = menu_loader

    def get_pedal_control(self) -> MenuControl:
        if "--count" in sys.argv:  # will be counting notes in python controller
            return CountMidiControl(self.in_port, self.send_conn, self.menu_loader)
        else:
            return MidiControl(self.in_port, self.send_conn, self.menu_loader)

    def get_screen_control(self) -> MenuControl:
        if ENV_USE_TEXT:
            return PyScreen(self.recv_conn, self.send_conn, self.menu_loader)

        if not os.path.isfile(ENV_ROOT_DIR + "/" + ConfigName.shared_lib):
            logging.error(f"Libarry {ConfigName.shared_lib} not found, using text mode")
            return PyScreen(self.recv_conn, self.send_conn, self.menu_loader)

        from mvc._ccscreen import CcScreen
        logging.info(f"Library {ConfigName.shared_lib} found, loading graphics mode")
        return CcScreen(self.recv_conn, self.send_conn, self.menu_loader, ENV_FRAME_BUFFER_ID)
