from multiprocessing import Queue
from textwrap import wrap
from threading import Thread
from time import sleep

from mvc.menuclient import MenuClient
from utils.util_screen import SCR_COLS
from utils.util_screen import get_screen_dict, get_default_dict

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
        self.__dic: dict = get_screen_dict(get_default_dict())
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

    def _client_stop(self) -> None:
        super()._client_stop()

    def _client_log(self, msg: str) -> None:
        print(f"{_CURSOR_MOVE}\n{msg}")

    def _client_redraw(self, dic: dict) -> None:
        assert "header" in dic
        assert "description" in dic
        assert "content" in dic
        assert "is_rec" in dic
        assert "len" in dic

        dic["header"] = dic["header"][:SCR_COLS].center(SCR_COLS)
        dic["description"] = '\n'.join([x.center(SCR_COLS) for x in wrap(dic["description"], SCR_COLS)])
        dic["content"] = '\n'.join([self.__add_color(x, dic["is_rec"]) for x in dic["content"].split('\n')])

        print(f'{_CURSOR_MOVE}{dic["header"]}{_CLEAN_TO_END}')
        print(dic["description"])
        print(dic["content"], flush=True)

        self.__dic = get_screen_dict(dic)

    def __updater(self):
        while self._alive:
            sleep(self.__dic["sleep_tm"])
            line = self.__dic["header"]
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
            print(f"{_CURSOR_MOVE}{line}", end='', flush=True)
