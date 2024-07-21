import os
from abc import ABC, abstractmethod
from configparser import ConfigParser
from multiprocessing import Queue
from time import sleep

from basic.midiinfo import MidiInfo
from utils.util_config import load_ini_section, convert_param
from utils.util_log import MY_LOG
from utils.util_name import AppName


class _MenuLoader:
    """ class loading menu mapping from INI files in a directory """

    def __init__(self, dname: str):
        if not os.path.isdir(dname):
            raise RuntimeError(f"Menu directory not found: {dname}. Check main.ini and local.ini files")
        self.__sect_idx: int = 0
        self.__section: str = AppName.play_section
        self.__dic = dict()
        fname1 = f"{dname}/navigate.ini"
        for fname in ["play.ini", "song.ini", "drum.ini", "serv.ini"]:
            fname2 = f"{dname}/{fname}"
            cfg = ConfigParser()
            read_lst = cfg.read([fname1, fname2])
            if len(read_lst) != 2:
                raise RuntimeError(f"Not all INI menu files loaded: {fname1}, {fname2}")
            tmp = {s: dict(cfg.items(s)) for s in cfg.sections()}
            self.__dic |= tmp
        MY_LOG.debug(f"Loaded menu\n: {self.__dic}")

    def get(self, key: str) -> str:
        sect_name = f"{self.__section}.{self.__sect_idx}"
        sect_dic = self.__dic.get(sect_name, dict())
        if key in sect_dic:
            return sect_dic[key]

        return ""

    def _menu_update(self, section: str) -> None:
        assert f"{section}.0" in self.__dic
        self.__section = section
        self.__sect_idx = 0

    def _section_update(self, k: int) -> None:
        lst = [x for x in self.__dic.keys() if self.__section in x]
        self.__sect_idx = (self.__sect_idx + k) % len(lst)

    def __str__(self):
        return f"{self.__section}.{self.__sect_idx}"


class MenuHost(_MenuLoader, ABC):
    """Translate notes to menu command and put into queue """

    def __init__(self, queue: Queue):
        self.__dic: dict = dict()
        dic = load_ini_section("MENU")
        dname = dic.get(AppName.menu_choice, "")
        dname = f"{AppName.menu_config_dir}/{dname}"
        _MenuLoader.__init__(self, dname)
        self.__queue: Queue = queue
        self._menu_update(AppName.play_section)
        self.__queue.put([AppName.client_redraw, self.__dic])
        self._midi_dict = MidiInfo().MIDI_DICT
        self._alive: bool = True

    @abstractmethod
    def is_broken(self) -> bool:
        raise RuntimeError("This method should NOT be called()")

    def host_start(self) -> None:
        MY_LOG.info(f"MenuHost start working")
        while self._alive and not self.is_broken():
            sleep(5)
        self.__queue.put([AppName.client_stop])
        MY_LOG.info(f"MenuHost stop working")

    def _menu_update(self, fname: str) -> None:
        super()._menu_update(fname)
        self.__dic["description"] = self.get(AppName.description)
        self.__dic["update_method"] = self.get(AppName.update_method)

    def _section_update(self, k: int) -> None:
        super()._section_update(k)
        self.__dic["description"] = self.get(AppName.description)
        self.__dic["update_method"] = self.get(AppName.update_method)

    def _send_command(self, note: int, velo: int) -> None:
        if note not in self._midi_dict:
            MY_LOG.error(f"MIDI note: {note} is not expected. Check main.ini file")

        menu_key: str = f"{self._midi_dict[note]}-{velo}"
        menu_cmd = self.get(menu_key)
        lst = menu_cmd.split(":")  # if there are many commands we need the list
        for cmd in lst:
            lst1 = cmd.split()  # method name and arguments if any
            self.__process_list(lst1)
        # after all commands send _redraw
        self.__queue.put([AppName.client_redraw, self.__dic])

    def __process_list(self, cmd: list) -> None:
        if not (cmd and isinstance(cmd, list)):
            return

        cmd = [cmd[0], *[convert_param(x) for x in cmd[1:]]]
        if cmd[0] == AppName.menu_update:
            self._menu_update(cmd[1])
        elif cmd[0] == AppName.section_update:
            self._section_update(cmd[1])
        elif cmd[0] == AppName.client_stop:
            self._alive = False
        else:
            MY_LOG.debug(f"MenuHost send command: {cmd}")
            self.__queue.put(cmd)


if __name__ == "__main__":
    pass
