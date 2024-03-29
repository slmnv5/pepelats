import os
from abc import abstractmethod
from configparser import ConfigParser
from multiprocessing import Queue
from threading import Event

from utils.utilconfig import ConfigName, find_path, load_ini_section
from utils.utillog import get_my_log
from utils.utilother import DrawInfo

my_log = get_my_log(__name__)


class MenuHost:
    """Translate menu command with parameters and sends to a connection. """

    def __init__(self, queue: Queue):
        dic = load_ini_section(find_path(ConfigName.main_ini), "MENU")
        dname = dic.get(ConfigName.menu_dir)
        dname = find_path(f"config/menu/{dname}")
        assert os.path.isdir(dname)
        self._menu_loader = _MenuLoader(dname)
        self._draw_info = DrawInfo()
        self.__queue = queue
        self._update_menu(ConfigName.play_section)
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
        self._sect_idx: int = 0
        self._section: str = ConfigName.play_section
        assert os.path.isdir(dname)
        self._dic = dict()
        files_lst = ["play.ini", "song.ini", "drum.ini", "serv.ini"]
        for fname in files_lst:
            fname1, fname2 = f"{dname}/navigate.ini", f"{dname}/{fname}"
            cfg = ConfigParser()
            read_lst = cfg.read([fname1, fname2])
            if len(read_lst) != 2:
                raise RuntimeError(f"Not all INI menu files wre loaded: {fname1}, {fname2}")
            dic = {s: dict(cfg.items(s)) for s in cfg.sections()}
            self._dic |= dic

    def get(self, key: str) -> str:
        sect_name = f"{self._section}.{self._sect_idx}"
        sect_dic = self._dic.get(sect_name, dict())
        if key in sect_dic:
            return sect_dic[key]

        my_log.debug(f"Did not find key: {key} in menu: {sect_name}")
        return ""

    def update_menu(self, section: str) -> None:
        assert f"{section}.0" in self._dic
        self._section = section
        self._sect_idx = 0

    def update_section(self, go_next: bool = True) -> None:
        lst = [x for x in self._dic.keys() if self._section in x]
        self._sect_idx += (1 if go_next else -1)
        self._sect_idx %= len(lst)

    def __str__(self):
        return f"{self._section}.{self._sect_idx}"


if __name__ == "__main__":
    ml = _MenuLoader(find_path("config/menu/button4"))
    print(ml.get("60-100"))
    print(ml.get("65-6"))
