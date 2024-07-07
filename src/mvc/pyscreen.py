import os
import time
from multiprocessing import Queue
from textwrap import wrap
from threading import Thread

from mvc.menuclient import MenuClient
from utils.utilconfig import KEEP_SCREEN
from utils.utillog import MYLOG
from utils.utilother import DrawInfo

if os.name == "posix":
    _UPDATES_PER_LOOP: float = 16
else:
    _UPDATES_PER_LOOP: float = 0.01

try:
    _COLS, _ROWS = os.get_terminal_size()
except OSError:
    _COLS, _ROWS = 30, 10

MYLOG.info(f"Text screen size: cols={_COLS} rows={_ROWS}")

# foreground, background ends with '40m'
_END_ALL: str = '\x1b[0m'

_RED_COLOR: str = '\x1b[1;31m'
_GREEN_COLOR: str = '\x1b[1;32m'
_YELLOW_COLOR: str = '\x1b[1;33m'
_BLUE_COLOR: str = '\x1b[1;34m'

_REVERSE_COLOR: str = '\x1b[7m'
_END_REVERSE: str = '\x1b[27m'


def get_with_color(line: str, is_rec: bool) -> str:
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


# print("\033c", end="")


class PyScreen(MenuClient):

    def __init__(self, q: Queue):
        MenuClient.__init__(self, q)
        Thread(target=self.__updater, name="updater", daemon=True).start()

    def _menu_client_redraw(self, draw_info: DrawInfo) -> None:
        self._di = draw_info
        if not KEEP_SCREEN:
            print("\033c", end="")  # clear screen
        draw_info.header = draw_info.header[:_COLS].center(_COLS)
        print(draw_info.header)
        lines = wrap(draw_info.description, _COLS)
        print(_BLUE_COLOR, end='')
        for line in [x for x in lines if x]:
            print(line)
        print(_END_ALL, end='')
        lines = draw_info.content.split('\n')
        for line in lines:
            line = line[:_COLS]
            line = get_with_color(line, draw_info.is_rec)
            print(line)
        # print("", end="", flush=True)

    def __updater(self):
        while True:
            di = self._di
            line = di.header
            time.sleep(di.loop_seconds / _UPDATES_PER_LOOP)

            di.loop_position += 1.0 / _UPDATES_PER_LOOP
            if di.loop_position >= 1.0:
                di.loop_position = 0.0

            if di.max_loop_factor > 1:
                di.max_loop_position += 1.0 / _UPDATES_PER_LOOP / di.max_loop_factor
                if di.max_loop_position >= 1:
                    di.max_loop_position = 0
                pos = round(di.max_loop_position * _COLS)
                line = line[:pos] + '*' + line[pos + 1:]

            pos = round(di.loop_position * _COLS)
            line = _REVERSE_COLOR + line[:pos] + _END_REVERSE + line[pos:]

            # all starts at 1, 1
            print(f"\033[1;1H{line}", end='', flush=True)
