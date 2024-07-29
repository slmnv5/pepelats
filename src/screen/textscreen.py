from multiprocessing import Queue
from textwrap import wrap
from threading import Thread
from time import sleep

from basic.audioinfo import AudioInfo
from screen.menuclient import MenuClient
from utils.util_name import AppName
from utils.util_screen import SCR_COLS
from utils.util_screen import get_default_dict

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

_UPDATES_PER_LOOP: int = 16


def _recalc_dic(dic: dict) -> None:
    dic["sleep_tm"] = dic["len"] / AudioInfo().SD_RATE / _UPDATES_PER_LOOP
    dic["pos"] = (dic["idx"] % dic["len"]) / dic["len"]
    dic["delta"] = 1 / _UPDATES_PER_LOOP
    if dic["max_loop_len"] > dic["len"]:
        dic["max_loop_pos"] = (dic["idx"] % dic["max_loop_len"]) / dic["max_loop_len"]
        dic["max_loop_delta"] = 1 / _UPDATES_PER_LOOP / dic["max_loop_len"] * dic["len"]
    else:
        dic["max_loop_pos"], dic["max_loop_delta"] = 0, 0


class TextScreen(MenuClient):

    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        self.__dic: dict = get_default_dict()
        _recalc_dic(self.__dic)
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

    def _client_redraw(self, dic: dict) -> None:
        dic[AppName.header] = dic[AppName.header][:SCR_COLS].center(SCR_COLS)
        dic[AppName.description] = '\n'.join([x.center(SCR_COLS) for x in wrap(dic[AppName.description], SCR_COLS)])
        dic[AppName.content] = '\n'.join([self.__add_color(x, dic["is_rec"]) for x in dic[AppName.content].split('\n')])

        print(f'{_CURSOR_MOVE}{dic[AppName.header]}{_CLEAN_TO_END}')
        print(dic[AppName.description])
        print(dic[AppName.content], flush=True)

        self.__dic = dic
        _recalc_dic(self.__dic)

    def __update(self):
        while self._alive:
            sleep(self.__dic["sleep_tm"])
            line = self.__dic[AppName.header]
            delta = self.__dic["max_loop_delta"]
            if delta > 0:
                pos = (self.__dic["max_loop_pos"] + delta) % 1
                self.__dic["max_loop_pos"] = pos
                pos = round(pos * SCR_COLS)
                line = line[:pos] + '▒' + line[pos + 1:]

            delta = self.__dic["delta"]
            pos = (self.__dic["pos"] + delta) % 1
            self.__dic["pos"] = pos
            pos = round(pos * SCR_COLS)  # shown by inverse color
            line = _REV_CLR + line[:pos] + _END_ALL + line[pos:]
            print(f"{_CURSOR_MOVE}{line}", end="", flush=True)
