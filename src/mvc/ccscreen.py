from multiprocessing import Queue
from random import randint
from textwrap import wrap
from time import sleep

from mvc._touchscreen import TouchScreen
from mvc.menuclient import MenuClient
from mvc.menuhost import MenuHost
from utils.utilconfig import VERBOSE_MODE
from utils.utillog import get_my_log
from utils.utilname import generate_name
from utils.utilother import DrawInfo

my_log = get_my_log(__name__)

GREY_COLOR: list[int] = [150, 150, 150]
WHITE_COLOR: list[int] = [250, 250, 250]
YELLOW_COLOR: list[int] = [210, 210, 0]
GREEN_COLOR: list[int] = [0, 255, 0]
RED_COLOR: list[int] = [255, 0, 0]


class CcScreen(MenuClient, MenuHost, TouchScreen):
    """ C++ shared library used for graphics and touch input via TouchScreen"""

    def __init__(self, recv_q: Queue, send_q: Queue, fb_id: str):
        fb_id: int = int(fb_id)
        TouchScreen.__init__(self, fb_id)
        MenuClient.__init__(self, recv_q)
        MenuHost.__init__(self, send_q)

        log_level = 0 if VERBOSE_MODE else 4
        result = self._set_log_level(log_level)
        my_log.info(f"Set logging level: {log_level} for shared library, result: {result}")

    def start(self) -> None:
        my_log.info(f"{self.__class__.__name__} working as MenuHost")
        while True:
            msg: str = self._get_click_event_word()
            self._menuhost_send(msg)

    def _redraw(self, draw_info: DrawInfo) -> None:
        if not draw_info:
            return
        self._set_loop(draw_info.loop_seconds, draw_info.loop_position, draw_info.is_rec)
        self._clear_screen()
        self._set_row_text(0, draw_info.header, *WHITE_COLOR)  # x, y, red, green, blue
        k: int = 1
        lines = wrap(draw_info.description, self._get_cols())
        for line in [x for x in lines if x]:
            self._set_row_text(k, line, *GREY_COLOR)  # x, y, red, green, blue
            k += 1

        for line in draw_info.content.split(sep='\n'):
            if not line:
                continue
            if line[0] == '*':
                color = (RED_COLOR if draw_info.is_rec else GREEN_COLOR)
            elif line[0] == '~':
                color = YELLOW_COLOR
            else:
                color = GREY_COLOR

            self._set_row_text(k, line, *color)
            k += 1

    def _gui_test(self):
        for i in range(150):
            sleep(0.2)
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
