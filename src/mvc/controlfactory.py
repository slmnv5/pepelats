import sys
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from typing import Union

from mvc import CountMidiControl
from mvc import MidiControl
from mvc.menucontrol import MenuLoader, MenuControl
from mvc._pyscreen import PyScreen
from utils.log import LOGGER


class ControlFactory:
    def __init__(self, in_port, recv_conn: Connection, send_conn: Connection, menu_loader: MenuLoader):
        self.in_port = in_port
        self.send_conn = send_conn
        self.recv_conn = recv_conn
        self.menu_loader = menu_loader
        self.__failed_gui = False

    def get_pedal_control(self) -> MenuControl:
        if "--count" in sys.argv:  # will be counting notes in python controller
            return CountMidiControl(self.in_port, self.send_conn, self.menu_loader)
        else:
            return MidiControl(self.in_port, self.send_conn, self.menu_loader)

    def get_screen_control(self, gui: bool) -> MenuControl:
        if gui:
            gui_scvreen = self.__get_gui_screen()
            if gui_scvreen:
                return gui_scvreen
        return PyScreen(self.recv_conn, self.send_conn, self.menu_loader)

    def __get_gui_screen(self) -> Union[MenuControl, None]:
        if self.__failed_gui:
            LOGGER.warn("Had an error with 'touchscr5.so'")
            return None
        # noinspection PyBroadException
        try:
            from mvc._ccscreen import CcScreen
            return CcScreen(self.recv_conn, self.send_conn, self.menu_loader)
        except Exception:
            LOGGER.warn("Error loading C++ shared library 'touchscr5.so'")
            self.__failed_gui = True
            return None
