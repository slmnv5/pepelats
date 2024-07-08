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

# foreground, background ends with '40m'
_END_ALL: str = '\x1b[0m'

_RED_COLOR: str = '\x1b[1;31m'
_GREEN_COLOR: str = '\x1b[1;32m'
_YELLOW_COLOR: str = '\x1b[1;33m'
_BLUE_COLOR: str = '\x1b[1;34m'

_REVERSE_COLOR: str = '\x1b[7m'
_END_REVERSE: str = '\x1b[27m'

_UNDER_LINE: str = '\x1b[4m'
_UNDER_END: str = '\x1b[24m'


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
            line = get_with_color(line, draw_info.is_rec)
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
                line = _UNDER_LINE + line[:pos] + _UNDER_END + line[pos:]

            pos = round(self._di.loop_position * SCR_COLS)
            line = _REVERSE_COLOR + line[:pos] + _END_REVERSE + line[pos:]

            print(f"\033[1;1H{line}", end='', flush=True)
