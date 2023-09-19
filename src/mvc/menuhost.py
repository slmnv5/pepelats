import os
from abc import abstractmethod
from configparser import ConfigParser
from multiprocessing import Queue
from threading import Event

from utils.utilconfig import ConfigName, find_path
from utils.utillog import get_my_log
from utils.utilother import DrawInfo

my_log = get_my_log(__name__)


class MenuHost:
    """Translate menu command with parameters and sends to a connection. """

    def __init__(self, queue: Queue):
        self._menu_loader = _MenuLoader(find_path("config/menu"))
        self._menu_loader.update_menu()
        self._draw_info = DrawInfo()
        self.__queue = queue
        self._update_menu("play.ini")
        self.__queue.put([ConfigName.client_redraw, self._draw_info])

    @abstractmethod
    def start(self) -> None:
        my_log.info(f"{self.__class__.__name__} working as MenuHost")
        Event().wait()

    def _update_menu(self, fname: str):
        self._menu_loader.update_menu(fname)
        self._draw_info.description = self._menu_loader.get(ConfigName.description)
        self._draw_info.update_method = self._menu_loader.get(ConfigName.update_method)

    def _update_section(self, go_next: bool):
        self._menu_loader.update_section(go_next)
        self._draw_info.description = self._menu_loader.get(ConfigName.description)
        self._draw_info.update_method = self._menu_loader.get(ConfigName.update_method)

    def _menuhost_send(self, key: str) -> None:
        # map note to command in JSON menu files
        menu_str = self._menu_loader.get(key)
        if not menu_str:
            return

        lst = menu_str.split(":")  # if there are many commands we need the list
        for cmd in lst:
            lst1 = cmd.split()  # method name and arguments if any
            self.__process_list(lst1)
        # after all commands send _redraw
        self.__queue.put([ConfigName.client_redraw, self._draw_info])

    def __process_list(self, cmd: list) -> None:
        if not (cmd and type(cmd) == list):
            return
        elif cmd[0] == "_update_menu":
            self._update_menu(cmd[1])
        elif cmd[0] == "_prev_section":
            self._update_section(False)
        elif cmd[0] == "_next_section":
            self._update_section(True)
        else:
            for k in range(1, len(cmd)):
                if cmd[k].strip('+-').isdigit():
                    cmd[k] = int(cmd[k])
                elif cmd[k].strip('+-').replace('.', '', 1).isdigit():
                    cmd[k] = float(cmd[k])

            my_log.debug(f"{self.__class__.__name__} send command: {cmd}")
            self.__queue.put(cmd)


class _MenuLoader:
    """ class loading mapping dict. from JSON files
    It parses directory for JSON files """

    def __init__(self, dname: str):
        assert os.path.isdir(dname)
        self._fname: str = ""
        self._sect_id: int = 0
        self._dic: dict[str, dict[str, dict[str, any]]] = dict()
        for fname in [x for x in os.listdir(dname) if x.endswith('.ini')]:
            cfg = ConfigParser()
            cfg.read(dname + os.sep + fname)
            my_log.info(f"Loading control config from {fname}")
            self._dic[fname] = {s: dict(cfg.items(s)) for s in cfg.sections()}

        self._fname = list(self._dic.keys())[0]

    def get(self, key: str) -> str:
        lst = list(self._dic[self._fname])
        sect: str = lst[self._sect_id]
        try:
            return self._dic[self._fname][sect][key]
        except KeyError:
            my_log.debug(f"Did not find menu: {self._fname}:{sect}:{key}")
            return ""

    def update_menu(self, fname: str = None) -> None:
        if not fname:
            self._fname = list(self._dic)[0]
        else:
            assert fname in list(self._dic)
            self._fname = fname
        self._sect_id = 0

    def update_section(self, go_next: bool = True) -> None:
        lst = list(self._dic[self._fname])
        self._sect_id += (1 if go_next else -1)
        self._sect_id %= len(lst)

    def __str__(self):
        return f"{self._fname}:{self._sect_id}"
