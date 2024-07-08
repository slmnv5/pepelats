import os
import time
from multiprocessing import Queue
from textwrap import wrap
from threading import Thread

from mvc.menuclient import MenuClient
from utils.utilconfig import SCR_COLS
from utils.utilother import DrawInfo

if os.name == "posix":
    _UPDATES_PER_LOOP: float = 16.0
else:
    _UPDATES_PER_LOOP: float = 0.01

_BLACK = 4
_RED = 31
_GREEN = 32
_YELLOW = 33
_BLUE = 34
_MAGENTA = 35
_CYAN = 36
_WHITE = 37


def _get_color_str(fg_color_id: int, bk_color_id: int) -> str:
    if fg_color_id and not bk_color_id:
        return f"\x1b[{fg_color_id}m"
    elif not fg_color_id and bk_color_id:
        return f"\x1b[{bk_color_id + 10}m"
    else:
        return f"\x1b[{fg_color_id};{bk_color_id + 10}m"


_END_ALL: str = '\x1b[0m'
_REVERSE_COLOR: str = '\x1b[7m'
_RED_COLOR: str = _get_color_str(_RED, 0)
_YELLOW_COLOR: str = _get_color_str(_YELLOW, 0)
_GREEN_COLOR: str = _get_color_str(_GREEN, 0)


def _get_with_color(line: str, is_rec: bool) -> str:
    if not line:
        return ""
    if line[0] == "*":
        if is_rec:
            return _RED_COLOR + line + _END_ALL
        else:
            return _GREEN_COLOR + line + _END_ALL
    elif line[0] == "~":
        return _YELLOW_COLOR + line + _END_ALL
    else:
        return line


class PyScreen(MenuClient):

    def __init__(self, q: Queue):
        MenuClient.__init__(self, q)
        self._di = DrawInfo()
        Thread(target=self.__updater, name="updater", daemon=True).start()

    def _menu_client_redraw(self, draw_info: DrawInfo) -> None:
        self._di = draw_info
        self._di.header = self._di.header[:SCR_COLS].center(SCR_COLS)

        print(f"\033[1;1H{self._di.header}")  # move cursor to line=1 and pos=1

        lines = wrap(draw_info.description, SCR_COLS)
        lines = [x.ljust(SCR_COLS) for x in lines]
        print('\n'.join(lines))

        lines = draw_info.content.split('\n')
        for line in lines:
            line = _get_with_color(line.ljust(SCR_COLS), draw_info.is_rec)
            print(line)
        print('\x1b[0J', end='')

    def __updater(self):
        while True:
            time.sleep(self._di.loop_seconds / _UPDATES_PER_LOOP)

            self._di.loop_position += 1.0 / _UPDATES_PER_LOOP
            if self._di.loop_position >= 1.0:
                self._di.loop_position = 0.0

            line = self._di.header
            if self._di.max_loop_factor > 1:
                self._di.max_loop_position += 1.0 / _UPDATES_PER_LOOP / self._di.max_loop_factor
                if self._di.max_loop_position >= 1:
                    self._di.max_loop_position = 0
                pos = round(self._di.max_loop_position * SCR_COLS)
                line = line[:pos] + '▒' + line[pos + 1:]

            pos = round(self._di.loop_position * SCR_COLS)  # shown by inverse background
            line = _REVERSE_COLOR + line[:pos] + _END_ALL + line[pos:]
            print(f"\033[1;1H{line}", end='', flush=True)
