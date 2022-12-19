import os
from abc import abstractmethod
# noinspection PyProtectedMember
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from typing import Dict, Union, List

from utils.config import ConfigName
from utils.log import DumbLog
from utils.utilother import FileFinder, JsonDict, DrawInfo


class MenuLoader:
    """ class loading mapping dict. from JSON files
    It parses directory for JSON files """

    def __init__(self, load_dir: str, map_name: str, map_id: str):
        ff = FileFinder(load_dir, True, ".json")
        self.__map_name: str = map_name
        self.__map_id: str = map_id
        self.__items: Dict[str, Dict[str, Dict]] = dict()

        for _ in range(ff.item_count):
            file: str = ff.get_full_name()
            item: str = ff.get_item()[:-len(ff.get_end_with())]
            ff.iterate(True)
            DumbLog.info(f"Loading control config from {file}")
            loader = JsonDict(file)
            default_dic = loader.get(ConfigName.default_config, dict())
            dic1 = dict()

            for key in [x for x in loader.dic() if x not in [ConfigName.default_config, ConfigName.comment]]:
                value = loader.get(key, None)
                assert type(value) == dict, f"Must be dictionary key={key} in file {item}"
                assert len(value) > 0, f"Dictionary must be non empty key={key} in file {item}"
                dic1[key] = dict(default_dic, **value)

            self.__items[item] = dic1

    def get(self, key: str) -> Union[List, str]:
        try:
            return self.__items[self.__map_name][self.__map_id][key]
        except KeyError:
            return ""

    def change_map(self, new_id: str, new_name: str) -> None:
        DumbLog.debug(f"{self.__class__.__name__} change_map: {new_id}, {new_name}")
        if new_name and new_id not in ["prev", "next"]:
            self.__map_name = new_name
        if new_id in ["prev", "next"]:
            lst = list(self.__items[self.__map_name])
            k = lst.index(self.__map_id)
            k += (1 if new_id == "next" else -1)
            k = 0 if k >= len(lst) else k
            k = len(lst) - 1 if k < 0 else k
            self.__map_id = lst[k]
        else:
            self.__map_id = new_id
        try:
            _ = self.__items[self.__map_name][self.__map_id]
        except IndexError:
            DumbLog.error(f"{self.__class__.__name__} change_map, incorrect id, name: {new_id}, {new_name}")

    def __str__(self):
        return self.__class__.__name__ + ": " + str(self.__items)


class MenuControl:
    """Translate menu command with parameters and sends to a connection. Use inner class to hold info """

    def __init__(self, send_conn: Connection, menu_loader: MenuLoader):
        self._menu_loader = menu_loader
        self.__s_conn = send_conn
        self.__redraw = DrawInfo()
        self.__prepare_redraw()
        self.__s_conn.send([ConfigName.send_redraw, self.__redraw])

    def __prepare_redraw(self):
        self.__redraw.text = self._menu_loader.get(ConfigName.text)
        self.__redraw.update_method = self._menu_loader.get(ConfigName.update_method)

    def _send(self, cmd: str) -> None:
        # map note to command in JSON menu files
        cmd = self._menu_loader.get(cmd)
        if cmd:
            self.__process_list(cmd)
            DumbLog.info(f"{self.__class__.__name__} sent command: {cmd}")

    def __process_list(self, cmd: list) -> None:
        if not cmd:
            return
        head, *tail = cmd
        if isinstance(head, list):
            self.__process_list(head)
            self.__process_list(tail)
        else:
            if head == ConfigName.change_map:
                self._menu_loader.change_map(tail[0], tail[1])
                self.__prepare_redraw()
                self.__s_conn.send([ConfigName.send_redraw, self.__redraw])
            elif head == ConfigName.stop_monitor:
                if os.name == "posix":
                    os.system("killall -9 python")
                else:
                    os.system("taskkill /F /IM python.exe")
            else:
                self.__s_conn.send(cmd)

    @abstractmethod
    def monitor(self):
        pass


if __name__ == "__main__":
    pass
