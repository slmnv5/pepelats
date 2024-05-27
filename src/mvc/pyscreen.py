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
_END_COLOR: str = '\x1b[0m'
_RED_COLOR: str = '\x1b[1;31m'
_GREEN_COLOR: str = '\x1b[1;32m'
_YELLOW_COLOR: str = '\x1b[1;33m'
_BLUE_COLOR: str = '\x1b[1;34m'
_REVERSE_COLOR: str = '\x1b[7m'


def get_with_color(line: str, is_rec: bool) -> str:
    if not line:
        return ""
    if line[0] == "*":
        if is_rec:
            return _RED_COLOR + line + _END_COLOR
        else:
            return _GREEN_COLOR + line + _END_COLOR
    elif line[0] == "~":
        return _YELLOW_COLOR + line + _END_COLOR
    else:
        return line


# print("\033c", end="")


class PyScreen(MenuClient):

    def __init__(self, q: Queue):
        MenuClient.__init__(self, q)
        self.__header: str = ""
        self.__loop_seconds: float = 1
        self.__loop_position: float = 0
        Thread(target=self.__updater, name="updater", daemon=True).start()

    def _redraw(self, draw_info: DrawInfo) -> None:
        if not draw_info:
            return
        self.__loop_position = draw_info.loop_position
        self.__loop_seconds = draw_info.loop_seconds

        if not KEEP_SCREEN:
            print("\033c", end="")  # clear screen
        self.__header = draw_info.header[:_COLS].center(_COLS)
        print(self.__header)
        lines = wrap(draw_info.description, _COLS)
        print(_BLUE_COLOR, end='')
        for line in [x for x in lines if x]:
            print(line)
        print(_END_COLOR, end='')
        lines = draw_info.content.split('\n')
        for line in lines:
            line = line[:_COLS]
            line = get_with_color(line, draw_info.is_rec)
            print(line)
        print("", end='', flush=True)

    def __updater(self):
        while True:
            time.sleep(self.__loop_seconds / _UPDATES_PER_LOOP)
            self.__loop_position += 1.0 / _UPDATES_PER_LOOP
            if self.__loop_position >= 1:
                self.__loop_position = 0

            pos = round(self.__loop_position * _COLS)
            line = '\x1b[7m' + self.__header[:pos] + '\x1b[0m' + self.__header[pos:]
            # all starts at 1, 1
            print(f"\033[1;1H{line}", end='', flush=True)
