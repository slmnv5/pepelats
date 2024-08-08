from multiprocessing import Queue
from textwrap import wrap
from threading import Thread
from time import sleep

from screen.basescreen import BaseScreen
from screen.menuclient import MenuClient
from utils.util_config import SCR_COLS
from utils.util_name import AppName

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


class TextScreen(BaseScreen, MenuClient):

    def __init__(self, queue: Queue):
        BaseScreen.__init__(self)
        MenuClient.__init__(self, queue)
        Thread(target=self.__update, name="update", daemon=True).start()

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

    # noinspection PyMethodMayBeStatic
    def _client_log(self, msg: str) -> None:
        print(f"{_CURSOR_MOVE}\n{msg}")

    def _client_stop(self) -> None:
        self._alive = False

    def _client_redraw(self, dic: dict) -> None:
        dic[AppName.header] = dic[AppName.header][:SCR_COLS].center(SCR_COLS)
        dic[AppName.description] = '\n'.join([x.center(SCR_COLS) for x in wrap(dic[AppName.description], SCR_COLS)])
        dic[AppName.content] = '\n'.join([self.__add_color(x, dic["is_rec"]) for x in dic[AppName.content].split('\n')])

        print(f'{_CURSOR_MOVE}{dic[AppName.header]}{_CLEAN_TO_END}')
        print(dic[AppName.description])
        print(dic[AppName.content], flush=True)

        super()._recalc_dic(dic)

    def __update(self):
        while self._alive:
            dic = self._get_dic()
            sleep(dic["sleep_tm"])
            line = dic[AppName.header]
            delta = dic["max_loop_delta"]
            if delta > 0:
                pos = (dic["max_loop_pos"] + delta) % 1
                dic["max_loop_pos"] = pos
                pos = round(pos * SCR_COLS)
                line = line[:pos] + '▒' + line[pos + 1:]

            delta = dic["delta"]
            pos = (dic["pos"] + delta) % 1
            dic["pos"] = pos
            pos = round(pos * SCR_COLS)  # shown by inverse color
            line = _REV_CLR + line[:pos] + _END_ALL + line[pos:]
            print(f"{_CURSOR_MOVE}{line}", end="", flush=True)
