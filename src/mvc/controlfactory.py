import os
import sys
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from mvc import CountMidiControl
from mvc import MidiControl
from mvc._pyscreen import PyScreen
from mvc.menucontrol import MenuLoader, MenuControl
from utils.log import DumbLog


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
        if not os.getenv("TEXT_SCREEN"):
            # noinspection PyBroadException
            try:
                from mvc._ccscreen import CcScreen
                return CcScreen(self.recv_conn, self.send_conn, self.menu_loader)
            except Exception:
                DumbLog.error("Cannot load C++ shared library 'touchscr5.so'")

        return PyScreen(self.recv_conn, self.send_conn, self.menu_loader)
