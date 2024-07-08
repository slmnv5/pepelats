import os
from configparser import ConfigParser
from multiprocessing import Queue
from time import sleep

from basic.midiinfo import MidiInfo
from utils.utilconfig import ConfigName, find_path, load_ini_section
from utils.utillog import MYLOG
from utils.utilother import DrawInfo


class MenuHost:
    """Translate menu command with parameters and sends to a connection. """

    def __init__(self, queue: Queue):
        dic = load_ini_section("MENU")
        dname = dic.get(ConfigName.menu_dir, "")
        dname = find_path(f"config/menu/{dname}")
        if not os.path.isdir(dname):
            raise RuntimeError(f"Directory not found: {dname}. Check main.ini and local.ini files")
        self._menu_loader = _MenuLoader(dname)
        self._di = DrawInfo()
        self.__queue = queue
        self._menu_update(ConfigName.play_section)
        self.__queue.put([ConfigName.menu_client_redraw, self._di])
        self.min_velo = MidiInfo().MIDI_MIN_VELO
        self.std_velo = MidiInfo().MIDI_STD_VELO
        self.midi_dict = MidiInfo().MIDI_DICT

    def _is_alive(self) -> bool:
        return True

    def start_menu_host(self) -> None:
        MYLOG.info(f"{self.__class__.__name__} start working as MenuHost")
        while True:
            sleep(5)
            if not self._is_alive():
                break
        MYLOG.info(f"{self.__class__.__name__} stop working as MenuHost")

    def _menu_update(self, fname: str):
        self._menu_loader.update_menu(fname)
        self._di.description = self._menu_loader.get(ConfigName.description)
        self._di.update_method = self._menu_loader.get(ConfigName.update_method)

    def _update_section(self, go_next: bool):
        self._menu_loader.update_section(go_next)
        self._di.description = self._menu_loader.get(ConfigName.description)
        self._di.update_method = self._menu_loader.get(ConfigName.update_method)

    def _send(self, note: int, velo: int) -> None:
        if note not in self.midi_dict:
            MYLOG.error(f"MIDI note: {note} is not expected. Check main.ini file")

        menu_key: str = f"{self.midi_dict[note]}-{velo}"
        menu_cmd = self._menu_loader.get(menu_key)
        if not menu_cmd:
            return

        lst = menu_cmd.split(":")  # if there are many commands we need the list
        for cmd in lst:
            lst1 = cmd.split()  # method name and arguments if any
            self.__process_list(lst1)
        # after all commands send _redraw
        self.__queue.put([ConfigName.menu_client_redraw, self._di])

    def __process_list(self, cmd: list) -> None:
        if not (cmd and isinstance(cmd, list)):
            return
        elif cmd[0] == "_menu_update":
            self._menu_update(cmd[1])
        elif cmd[0] == "_menu_prev_section":
            self._update_section(False)
        elif cmd[0] == "_menu_next_section":
            self._update_section(True)
        else:
            for k in range(1, len(cmd)):
                if cmd[k].strip('+-').isdigit():
                    cmd[k] = int(cmd[k])
                elif cmd[k].strip('+-').replace('.', '', 1).isdigit():
                    cmd[k] = float(cmd[k])

            MYLOG.debug(f"{self.__class__.__name__} send command: {cmd}")
            self.__queue.put(cmd)


class _MenuLoader:
    """ class loading mapping dict. from JSON files
    It parses directory for JSON files """

    def __init__(self, dname: str):
        self._sect_idx: int = 0
        self._section: str = ConfigName.play_section
        assert os.path.isdir(dname)
        self._dict = dict()
        fname1 = f"{dname}/navigate.ini"
        for fname in ["play.ini", "song.ini", "drum.ini", "serv.ini"]:
            fname2 = f"{dname}/{fname}"
            cfg = ConfigParser()
            read_lst = cfg.read([fname1, fname2])
            if len(read_lst) != 2:
                raise RuntimeError(f"Not all INI menu files wre loaded: {fname1}, {fname2}")
            tmp = {s: dict(cfg.items(s)) for s in cfg.sections()}
            self._dict |= tmp
        MYLOG.debug(f"Loaded menu\n: {self._dict}")

    def get(self, key: str) -> str:
        sect_name = f"{self._section}.{self._sect_idx}"
        sect_dic = self._dict.get(sect_name, dict())
        if key in sect_dic:
            return sect_dic[key]

        return ""

    def update_menu(self, section: str) -> None:
        assert f"{section}.0" in self._dict
        self._section = section
        self._sect_idx = 0

    def update_section(self, go_next: bool = True) -> None:
        lst = [x for x in self._dict.keys() if self._section in x]
        self._sect_idx += (1 if go_next else -1)
        self._sect_idx %= len(lst)

    def __str__(self):
        return f"{self._section}.{self._sect_idx}"


if __name__ == "__main__":
    ml = _MenuLoader(find_path("config/menu/4x2"))
    print(ml.get("60-100"))
    print(ml.get("65-6"))
