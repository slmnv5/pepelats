import time
from multiprocessing import Queue
from textwrap import wrap
from threading import Thread

from mvc.drawinfo import DrawInfo
from mvc.menuclient import MenuClient
from utils.utilscreen import SCR_COLS

_CLEAN_TO_END = '\x1b[0J'  # clean from cursor to end of screen
_CURSOR_MOVE = "\x1b[1;1H"  # move cursor to line=1 and pos=1

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
        self._sleep_tm: float = 10
        self._dic: dict = dict()
        Thread(target=self.__updater, name="updater", daemon=True).start()

    @staticmethod
    def __add_color(line: str, is_rec: bool) -> str:
        line = line.ljust(SCR_COLS)
        if line[0] == "*":
            if is_rec:
                return _RED_CLR + line + _END_ALL
            else:
                return _GRN_CLR + line + _END_ALL
        elif line[0] == "~":
            return _YEL_CLR + line + _END_ALL
        else:
            return line

    def _client_redraw(self, di: DrawInfo) -> None:
        di.header = di.header[:SCR_COLS].center(SCR_COLS)
        di.description = '\n'.join([x.center(SCR_COLS) for x in wrap(di.description, SCR_COLS)])
        di.content = '\n'.join([self.__add_color(x, di.is_rec) for x in di.content.split('\n')])

        print(f"{_CURSOR_MOVE}{di.header}{_CLEAN_TO_END}")
        print(di.description)
        print(di.content, flush=True)

        self._sleep_tm = di.get_sleep_tm()
        self._dic = di.get_dict()

    def __updater(self):
        while self._alive:
            time.sleep(self._sleep_tm)
            line = self._dic["header"]
            delta = self._dic["max_loop_delta"]
            if delta > 0:
                pos = (self._dic["max_loop_pos"] + delta) % 1
                self._dic["max_loop_pos"] = pos
                pos = round(pos * SCR_COLS)
                line = line[:pos] + '▒' + line[pos + 1:]

            delta = self._dic["delta"]
            pos = (self._dic["pos"] + delta) % 1
            self._dic["pos"] = pos
            pos = round(pos * SCR_COLS)  # shown by inverse color
            line = _REV_CLR + line[:pos] + _END_ALL + line[pos:]
            print(f"{_CURSOR_MOVE}{line}", end='', flush=True)
