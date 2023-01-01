import logging
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from random import randint
from textwrap import wrap
from threading import Thread
from typing import List

from mvc._touchscreen import TouchScreen
from mvc.menucontrol import MenuControl, MenuLoader
from utils.msgprocessor import MsgProcessor
from utils.utilconfig import LEVEL_DEBUG
from utils.utilname import generate_name
from utils.utilother import DrawInfo


class CcScreen(MsgProcessor, MenuControl, TouchScreen):
    """ C++ shared library used for graphics and touch input via TouchScreen"""

    def __init__(self, recv_conn: Connection, send_conn: Connection, menu_loader: MenuLoader, fb_id: str):
        fb_id: int = int(fb_id)
        TouchScreen.__init__(self, fb_id)
        MenuControl.__init__(self, send_conn, menu_loader)
        MsgProcessor.__init__(self, recv_conn, send_conn)
        Thread(target=self.process_messages, name="message_thread", daemon=True).start()

        if LEVEL_DEBUG:
            result = self._set_log_level(0)
        else:
            result = self._set_log_level(4)
        logging.info(f"Set debug level for shared library, result: {result}")

    def _send_redraw(self, redraw: DrawInfo) -> None:
        grey_color: List = [110, 110, 110]
        white_color: List = [127, 127, 127]

        logging.debug(f"Get redraw: {redraw}")
        self._set_loop(redraw.loop_seconds, redraw.loop_position, redraw.is_rec, redraw.is_stop)
        self._clear_screen()
        self._set_row_text(0, redraw.header, *white_color)  # x, y, red, green, blue
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
                color = ([127, 70, 70] if redraw.is_rec else [70, 127, 70])
            elif line[0] == '~':
                color = [127, 127, 70]
            self._set_row_text(k, line, *color)
            k += 1

    def monitor(self):
        while True:
            cmd: str = self._get_click_event_word()
            self._send(cmd)

    def _gui_test(self):
        for i in range(110):
            x = randint(0, 480)
            y = randint(0, 320)
            width = randint(10, 480 // 2)
            height = randint(10, 320 // 2)
            color = [randint(0, 255), randint(0, 255), randint(0, 255)]
            if i < 50:
                self._put_square(x, y, width, height, *color)
            elif i < 100:
                self._put_square_inv(x, y, width, height)
            else:
                row = y // 32
                name = generate_name()
                self._set_row_text(row, name, *color)


if __name__ == "__main__":
    pass
