import os
import sys
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from mvc import CountMidiControl
from mvc import MidiControl
from mvc._pyscreen import PyScreen
from mvc.menucontrol import MenuLoader, MenuControl
from utils.config import ConfigName, ROOT_DIR
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
        if not os.path.isfile(ROOT_DIR + "/" + ConfigName.shared_lib):
            DumbLog.warn("Libarry touchscr5.so not found, GUI not avalable, using text")
            return PyScreen(self.recv_conn, self.send_conn, self.menu_loader)

        # noinspection PyBroadException
        try:
            DumbLog.info("Library touchscr5.so found, loading GUI")
            from mvc._ccscreen import CcScreen
            fb_id: str = os.getenv("FRAME_BUFFER_ID", "1")
            return CcScreen(self.recv_conn, self.send_conn, self.menu_loader, fb_id)
        except Exception:
            DumbLog.error("Library touchscr5.so load error, GUI not avalable, using text")
            return PyScreen(self.recv_conn, self.send_conn, self.menu_loader)
