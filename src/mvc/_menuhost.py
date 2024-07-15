import os
from configparser import ConfigParser
from multiprocessing import Queue
from time import sleep

from basic.midiinfo import MidiInfo
from utils.utilconfig import ConfigName, load_ini_section
from utils.utillog import MyLog
from utils.utilother import DrawInfo


class _MenuLoader:
    """ class loading menu mapping from INI files in a directory """

    def __init__(self, dname: str):
        if not os.path.isdir(dname):
            raise RuntimeError(f"Menu directory not found: {dname}. Check main.ini and local.ini files")
        self._sect_idx: int = 0
        self._section: str = ConfigName.play_section
        self._dict = dict()
        fname1 = f"{dname}/navigate.ini"
        for fname in ["play.ini", "song.ini", "drum.ini", "serv.ini"]:
            fname2 = f"{dname}/{fname}"
            cfg = ConfigParser()
            read_lst = cfg.read([fname1, fname2])
            if len(read_lst) != 2:
                raise RuntimeError(f"Not all INI menu files loaded: {fname1}, {fname2}")
            tmp = {s: dict(cfg.items(s)) for s in cfg.sections()}
            self._dict |= tmp
        MyLog().debug(f"Loaded menu\n: {self._dict}")

    def get(self, key: str) -> str:
        sect_name = f"{self._section}.{self._sect_idx}"
        sect_dic = self._dict.get(sect_name, dict())
        if key in sect_dic:
            return sect_dic[key]

        return ""

    def _menu_update(self, section: str) -> None:
        assert f"{section}.0" in self._dict
        self._section = section
        self._sect_idx = 0

    def _section_update(self, k: int) -> None:
        lst = [x for x in self._dict.keys() if self._section in x]
        self._sect_idx = (self._sect_idx + k) % len(lst)

    def __str__(self):
        return f"{self._section}.{self._sect_idx}"


def convert_param(param):
    param = param.replace(' ', '')
    if param.strip('+-').isdigit():
        return int(param)
    elif param.strip('+-').replace('.', '', 1).isdigit():
        return float(param)
    else:
        return param


class MenuHost(_MenuLoader):
    """Translate notes to menu command and put into queue """

    def __init__(self, queue: Queue):
        dic = load_ini_section("MENU")
        dname = dic.get(ConfigName.menu_choice, "")
        dname = f"{ConfigName.menu_config_dir}/{dname}"
        _MenuLoader.__init__(self, dname)
        self._di = DrawInfo()
        self.__queue = queue
        self._menu_update(ConfigName.play_section)
        self.__queue.put([ConfigName.client_redraw, self._di])
        self.min_velo = MidiInfo().MIDI_MIN_VELO
        self.std_velo = MidiInfo().MIDI_STD_VELO
        self.midi_dict = MidiInfo().MIDI_DICT
        self.__alive: bool = True

    def _is_alive(self) -> bool:
        return self.__alive

    def start_menu_host(self) -> None:
        MyLog().info(f"{self.__class__.__name__} start working as MenuHost")
        while self._is_alive():
            sleep(5)
        self.__queue.put([ConfigName.client_stop])
        MyLog().info(f"{self.__class__.__name__} stop working as MenuHost")

    def _menu_update(self, fname: str) -> None:
        super()._menu_update(fname)
        self._di.description = self.get(ConfigName.description)
        self._di.update_method = self.get(ConfigName.update_method)

    def _section_update(self, k: int) -> None:
        super()._section_update(k)
        self._di.description = self.get(ConfigName.description)
        self._di.update_method = self.get(ConfigName.update_method)

    def _send(self, note: int, velo: int) -> None:
        if note not in self.midi_dict:
            MyLog().error(f"MIDI note: {note} is not expected. Check main.ini file")

        menu_key: str = f"{self.midi_dict[note]}-{velo}"
        menu_cmd = self.get(menu_key)
        lst = menu_cmd.split(":")  # if there are many commands we need the list
        for cmd in lst:
            lst1 = cmd.split()  # method name and arguments if any
            self.__process_list(lst1)
        # after all commands send _redraw
        self.__queue.put([ConfigName.client_redraw, self._di])

    def __process_list(self, cmd: list) -> None:
        if not (cmd and isinstance(cmd, list)):
            return

        cmd = [cmd[0], *[convert_param(x) for x in cmd[1:]]]
        if cmd[0] == ConfigName.menu_update:
            self._menu_update(cmd[1])
        elif cmd[0] == ConfigName.section_update:
            self._section_update(cmd[1])
        elif cmd[0] == ConfigName.client_stop:
            self.__alive = False
        else:
            MyLog().debug(f"{self.__class__.__name__} send command: {cmd}")
            self.__queue.put(cmd)


if __name__ == "__main__":
    pass
