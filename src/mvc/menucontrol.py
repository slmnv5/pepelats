import logging
import traceback
from abc import abstractmethod
# noinspection PyProtectedMember
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from typing import Dict, Union, List

from utils.utilconfig import ConfigName
from utils.utilother import FileFinder, JsonDict, DrawInfo


class MenuLoader:
    """ class loading mapping dict. from JSON files
    It parses directory for JSON files """

    def __init__(self, load_dir: str, map_name: str, map_id: str):
        ff = FileFinder(load_dir, True, ".json")
        self.__map_name: str = map_name
        self.__map_id: str = map_id
        self.__items: Dict[str, Dict[str, Dict]] = dict()

        for _ in range(ff.item_count()):
            file: str = ff.get_full_name()
            item: str = ff.get_item()[:-len(ff.get_end_with())]
            ff.iterate(True)
            logging.info(f"Loading control config from {file}")
            loader = JsonDict(file)
            default_dic = loader.get(ConfigName.default_config, dict())
            dic1: Dict[str, Dict] = dict()

            for key in [x for x in loader.dict() if x not in [ConfigName.default_config, ConfigName.comment]]:
                dic2 = loader.get(key, None)
                assert type(dic2) == dict, f"Must be dictionary key={key} in file {item}"
                assert len(dic2) > 0, f"Dictionary must be non empty key={key} in file {item}"
                description: str = default_dic.get("description", "") + " " + dic2.get("description", "")
                dic1[key] = dict(default_dic, **dic2)
                dic1[key]["description"] = description

            self.__items[item] = dic1

    def get(self, key: str) -> Union[List, str]:
        try:
            return self.__items[self.__map_name][self.__map_id][key]
        except KeyError:
            return ""

    def change_map(self, new_name: str, new_id: str) -> None:
        logging.debug(f"{self.__class__.__name__} change_map: {new_name} {new_id}")
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
            logging.error(f"{self.__class__.__name__} change_map, incorrect id, name: {new_id}, {new_name}")

    def __str__(self):
        return f"{self.__map_name}:{self.__map_id}"


class MenuControl:
    """Translate menu command with parameters and sends to a connection. Use inner class to hold info """

    def __init__(self, send_conn: Connection, menu_loader: MenuLoader):
        self._menu_loader = menu_loader
        self.__s_conn = send_conn
        self.__redraw = DrawInfo()
        self._prepare_redraw("", "")

    def _prepare_redraw(self, new_name: str, new_id: str):
        if new_id or new_id:
            self._menu_loader.change_map(new_name, new_id)
        self.__redraw.text = self._menu_loader.get(ConfigName.text)
        self.__redraw.update_method = self._menu_loader.get(ConfigName.update_method)
        self.__s_conn.send([ConfigName.send_redraw, self.__redraw])

    def _send(self, cmd: str) -> None:
        # map note to command in JSON menu files
        cmd1 = self._menu_loader.get(cmd)
        if not cmd1:
            return
        if isinstance(cmd1, str):
            cmd1 = self._menu_loader.get(cmd1)
        if isinstance(cmd1, list):
            self.__process_list(cmd1)
            logging.info(f"{self.__class__.__name__} sent command: {cmd1}")
        else:
            logging.error(f"{self._menu_loader} menu command is NOT a list: {cmd} and {cmd1}")

    def __process_list(self, cmd: list) -> None:
        if not cmd:
            return
        head, *tail = cmd
        head_type = type(head)
        if head_type not in [list, str]:
            logging.error(f"{self._menu_loader} menu command is NOT a list or string: {cmd}")

        if head_type == list:
            self.__process_list(head)
            self.__process_list(tail)
        elif hasattr(self, head):
            method_name = head
            params = tail
            # noinspection PyBroadException
            try:
                method = getattr(self, method_name)
                method(*params)
            except Exception:
                logging.error(f"{self.__class__.__name__} in: {method_name} error: {traceback.format_exc()}")
        else:
            self.__s_conn.send(cmd)

    @abstractmethod
    def monitor(self):
        pass


if __name__ == "__main__":
    pass
