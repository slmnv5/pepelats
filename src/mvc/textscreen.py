import time
from multiprocessing import Queue
from textwrap import wrap
from threading import Thread

from mvc.drawinfo import DrawInfo
from mvc.menuclient import MenuClient
from utils.utilscreen import SCR_COLS

_CLEAN_TO_END = '\x1b[0J'  # clean from cursor to end of screen
_CURSOR_MOVE = ""  # "\x1b[1;1H"  # move cursor to line=1 and pos=1

_BLACK = 30
_RED = 31
_GREEN = 32
_YELLOW = 33
_BLUE = 34
_MAGENTA = 35
_CYAN = 36
_WHITE = 37

_END_ALL: str = '\x1b[0m'
_REV_CLR: str = '\x1b[7m'
_RED_CLR: str = f"\x1b[1;{_RED}m"
_YEL_CLR: str = f"\x1b[1;{_YELLOW}m"
_GRN_CLR: str = f"\x1b[1;{_GREEN}m"
_BLU_CLR: str = f"\x1b[1;{_BLUE}m"


class TextScreen(MenuClient):

    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        Thread(target=self.__updater, name="updater", daemon=True).start()

    def __add_color(self, line: str) -> str:
        line = line.ljust(SCR_COLS)
        if line[0] == "*":
            if self._di.is_rec:
                return _RED_CLR + line + _END_ALL
            else:
                return _GRN_CLR + line + _END_ALL
        elif line[0] == "~":
            return _YEL_CLR + line + _END_ALL
        else:
            return line

    def _client_redraw(self, di: DrawInfo) -> None:
        super()._client_redraw(di)
        self._di.header = di.header[:SCR_COLS].center(SCR_COLS)
        self._di.description = '\n'.join([x.center(SCR_COLS) for x in wrap(di.description, SCR_COLS)])
        self._di.content = '\n'.join([self.__add_color(x) for x in di.content.split('\n')])

        print(f"{_CURSOR_MOVE}{self._di.header}{_CLEAN_TO_END}")
        print(self._di.description)
        print(self._di.content, flush=True)

    def __updater(self):
        while self._alive:
            time.sleep(self._di.sleep)
            line = self._di.header
            self._di.pos += self._di.part_delta
            if self._di.pos > 1:
                self._di.pos = 0

            if self._di.max_factor > 1:
                self._di.max_pos += self._di.max_delta
                if self._di.max_pos > 1:
                    self._di.max_pos = 0
                pos = round(self._di.max_pos * SCR_COLS)
                line = line[:pos] + '▒' + line[pos + 1:]

            pos = round(self._di.pos * SCR_COLS)  # shown by inverse color
            line = _REV_CLR + line[:pos] + _END_ALL + line[pos:]
            print(f"{_CURSOR_MOVE}{line}", end='', flush=True)
