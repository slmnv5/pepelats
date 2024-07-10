import os
import time
from multiprocessing import Queue
from textwrap import wrap
from threading import Thread

from basic.audioinfo import AudioInfo
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


def _get_color_str(fg_color_id: int, bk_color_id: int, bold: bool = True) -> str:
    bld: int = 1 if bold else 2
    if fg_color_id and not bk_color_id:
        return f"\x1b[{bld};{fg_color_id}m"
    elif not fg_color_id and bk_color_id:
        return f"\x1b[{bld};{bk_color_id + 10}m"
    else:
        return f"\x1b[{bld};{fg_color_id};{bk_color_id + 10}m"


_END_ALL: str = '\x1b[0m'
_REV_CLR: str = '\x1b[7m'
_RED_CLR: str = _get_color_str(_RED, 0)
_YEL_CLR: str = _get_color_str(_YELLOW, 0)
_GRN_CLR: str = _get_color_str(_GREEN, 0)
_BLU_CLR: str = _get_color_str(_BLUE, 0)


def _get_with_color(line: str, is_rec: bool) -> str:
    if not line:
        return ""
    if line[0] == "*":
        if is_rec:
            return _RED_CLR + line + _END_ALL
        else:
            return _GRN_CLR + line + _END_ALL
    elif line[0] == "~":
        return _YEL_CLR + line + _END_ALL
    else:
        return line


class PyScreen(MenuClient):

    def __init__(self, q: Queue):
        MenuClient.__init__(self, q)
        self._line: str = ""
        self._pos: float = 0
        self._max_pos: float = 0
        self._max_factor: float = 1.0
        self._delta: float = 1.0 / _UPDATES_PER_LOOP
        self._delta_max: float = self._delta
        self._sleep: float = 10.0
        Thread(target=self.__updater, name="updater", daemon=True).start()

    def _menu_client_redraw(self, di: DrawInfo) -> None:
        self._pos = (di.idx % di.part_len) / di.part_len
        self._max_factor = di.max_loop_len / di.part_len
        self._max_pos = (di.idx % di.max_loop_len) / di.max_loop_len
        self._delta_max = self._delta / self._max_factor
        self._sleep = di.part_len / AudioInfo().SD_RATE / _UPDATES_PER_LOOP
        self._line = di.header[:SCR_COLS].center(SCR_COLS)

        print(f"\x1b[1;1H{self._line}")  # move cursor to line=1 and pos=1

        lines = wrap(di.description, SCR_COLS)
        lines = [x.ljust(SCR_COLS) for x in lines]
        print(_BLU_CLR, '\n'.join(lines), _END_ALL, sep='')

        lines = di.content.split('\n')
        for line in lines:
            line = _get_with_color(line.ljust(SCR_COLS), di.is_rec)
            print(line)
        print('\x1b[0J', end='', flush=True)

    def __updater(self):
        while True:
            time.sleep(self._sleep)
            line = self._line
            self._pos += self._delta
            if self._pos > 1:
                self._pos = 0

            if self._max_factor > 1:
                self._max_pos += self._delta_max
                if self._max_pos > 1:
                    self._max_pos = 0
                pos = round(self._max_pos * SCR_COLS)
                line = line[:pos] + '▒' + line[pos + 1:]

            pos = round(self._pos * SCR_COLS)  # shown by inverse color
            line = _REV_CLR + line[:pos] + _END_ALL + line[pos:]
            print(f"\x1b[1;1H{line}", end='', flush=True)
