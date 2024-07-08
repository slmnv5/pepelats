import os
import time
from multiprocessing import Queue
from textwrap import wrap
from threading import Thread

from mvc.menuclient import MenuClient
from utils.utilconfig import KEEP_SCREEN, SCR_COLS
from utils.utilother import DrawInfo

if os.name == "posix":
    _UPDATES_PER_LOOP: float = 16
else:
    _UPDATES_PER_LOOP: float = 0.01

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
        self._di = DrawInfo()
        self._line1: str = ''
        self._line2: str = ''
        Thread(target=self.__updater, name="updater", daemon=True).start()

    def _menu_client_redraw(self, draw_info: DrawInfo) -> None:
        self._di = draw_info
        self._line1 = draw_info.header[:SCR_COLS].center(SCR_COLS)

        print("\033[2;1H", end='')  # move cursor to line and position
        if not KEEP_SCREEN:
            print("\033[0J", end="")  # clear from cursor to end of screen

        lst: list[str] = wrap(draw_info.description, SCR_COLS)
        self._line2 = lst[0].center(SCR_COLS)

        print('\n'.join(lst), sep='')
        lines = draw_info.content.split('\n')
        for line in lines:
            line = line[:SCR_COLS]
            line = get_with_color(line, draw_info.is_rec)
            print(line)

    def __updater(self):
        while True:
            time.sleep(self._di.loop_seconds / _UPDATES_PER_LOOP)

            self._di.loop_position += 1.0 / _UPDATES_PER_LOOP
            if self._di.loop_position >= 1.0:
                self._di.loop_position = 0.0

            if self._di.max_loop_factor > 1:
                self._di.max_loop_position += 1.0 / _UPDATES_PER_LOOP / self._di.max_loop_factor
                if self._di.max_loop_position >= 1:
                    self._di.max_loop_position = 0
                pos = round(self._di.max_loop_position * SCR_COLS)
                line = _REVERSE_COLOR + self._line2[:pos] + _END_REVERSE + self._line2[pos:]
                print(f"\033[2;1H{line}", end='')

            pos = round(self._di.loop_position * SCR_COLS)
            line = _REVERSE_COLOR + self._line1[:pos] + _END_REVERSE + self._line1[pos:]
            print(f"\033[1;1H{line}", end='', flush=True)
