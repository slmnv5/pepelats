import sys
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from mvc import CountMidiControl
from mvc import MidiControl
from mvc.ccscreen import CcScreen
from mvc.menucontrol import MenuLoader
from mvc.pyscreen import PyScreen
from utils.log import LOGGER


class ControlFactory:
    def __init__(self, in_port, recv_conn: Connection, send_conn: Connection, menu_loader: MenuLoader):
        self.in_port = in_port
        self.send_conn = send_conn
        self.recv_conn = recv_conn
        self.menu_loader = menu_loader
        self.__failed_gui = False

    def get_pedal_control(self):
        if "--count" in sys.argv:  # will be counting notes in python controller
            m_ctrl = CountMidiControl(self.midi_in, self.send_looper, self.menu_loader)
        else:
            m_ctrl = MidiControl(self.midi_in, self.send_looper, self.menu_loader)

    def get_screen_control(self, gui: bool):
        if gui:
            if not self.__get_gui_screen():
                return PyScreen(self.recv_view)
        else:
            return PyScreen(self.recv_view)

    def __get_gui_screen(self):
        if self.__failed_gui:
            return None
        # noinspection PyBroadException
        try:
            return CcScreen(self.recv_conn, self.send_conn, self.menu_loader)
        except Exception:
            LOGGER.warn("Error loading C++ shared library 'touchscr5.so'")
            self.__failed_gui = True
            return None
