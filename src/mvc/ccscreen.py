import os
import sys
import time
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from multiprocessing.connection import Pipe
from textwrap import wrap
from threading import Thread
from typing import List

from mvc._touchscreen import TouchScreen
from mvc.menucontrol import MenuControl, MenuLoader
from utils.log import LOGGER
from utils.utilother import MsgProcessor, DrawInfo

LVL_DEBUG_LIB = "--debug" in sys.argv or "--info" in sys.argv


class CcScreen(MsgProcessor, MenuControl, TouchScreen):
    """ C++ shared library is used for graphics and touch input via TouchScreen"""

    def __init__(self, recv_conn: Connection, send_conn: Connection, menu_loader: MenuLoader):
        fb_id_str: str = os.getenv("FRAME_BUFFER_ID", "1")
        fb_id = int(fb_id_str)
        TouchScreen.__init__(self, fb_id)
        MenuControl.__init__(self, send_conn, menu_loader)
        MsgProcessor.__init__(self, recv_conn, send_conn)
        Thread(target=self.monitor, name="monitor_thread", daemon=True).start()

        if LVL_DEBUG_LIB:
            result = self._set_log_level(0)
        else:
            result = self._set_log_level(4)
        LOGGER.info(f"Set debug level for shared library, result: {result}")

    def _send_redraw(self, redraw: DrawInfo) -> None:
        grey_color: List = [100, 100, 100]
        LOGGER.debug(f"Get redraw: {redraw}")
        self._set_loop(redraw.loop_seconds, redraw.loop_position, redraw.is_rec, redraw.is_stop)
        self._clear_screen()
        self._set_row_text(0, redraw.header, *grey_color)  # x, y, red, green, blue
        k: int = 1
        lines = wrap(redraw.text, self._get_cols())
        for line in [x for x in lines if x]:
            self._set_row_text(k, line, *grey_color)  # x, y, red, green, blue
            k += 1

        for line in redraw.content.split(sep='\n'):
            color: List = grey_color
            if not len(line):
                continue
            if line[0] == '*':
                color = ([127, 30, 30] if redraw.is_rec else [30, 127, 30])
            elif line[0] == '~':
                color = [127, 127, 0]
            k += 1
            self._set_row_text(k, line, *color)

    def monitor(self):
        while True:
            cmd: str = self._get_click_event_word()
            self._send(cmd)


if __name__ == "__main__":
    def test1():
        recv_view, send_view = Pipe(False)  # screen update messages
        menu_loader = MenuLoader("config/menu", "play", "0")
        scr_view = CcScreen(recv_view, send_view, menu_loader)
        Thread(target=scr_view.process_messages, daemon=True).start()
        time.sleep(8)
