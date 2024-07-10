import os
import time
from multiprocessing import Queue

from control._songctrl import SongCtrl
from drum.bufferdrum import EuclidDrum, StyleDrum
from drum.loopdrum import LoopDrum
from drum.mididrum import MidiDrum
from mvc.menuclient import MenuClient
from utils.utilconfig import ConfigName
from utils.utilconfig import load_ini_section, find_path, update_ini_section
from utils.utillog import MyLog
from utils.utilother import DrawInfo, FileFinder


class Looper(MenuClient, SongCtrl):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_q: Queue, send_q: Queue):
        self._di = DrawInfo()
        MenuClient.__init__(self, recv_q)
        SongCtrl.__init__(self)
        self.__send_q = send_q
        self.drum_create(0)

    def drum_create(self, bar_len: int, **kwargs) -> None:
        self.menu_client_queue(['_drum_create', bar_len, {**kwargs}])

    def _drum_create(self, bar_len: int, drum_info: dict[str: any]) -> None:
        drum_type: str = drum_info.get(ConfigName.drum_type, self._drum.get_class_name())

        if drum_type == ConfigName.EuclidDrum:
            self._drum = EuclidDrum()
        elif drum_type == ConfigName.StyleDrum:
            self._drum = StyleDrum()
        elif drum_type == ConfigName.MidiDrum:
            self._drum = MidiDrum()
        elif drum_type == ConfigName.LoopDrum:
            self._drum = LoopDrum(self._song.get_list()[0])
        else:
            self._drum = StyleDrum()

        config: str = drum_info.get(ConfigName.drum_config)
        self._drum.set_config(config)
        volume = drum_info.get(ConfigName.drum_volume)
        if volume:
            self._drum.set_volume(volume)
        par = drum_info.get(ConfigName.drum_par)
        if par:
            self._drum.set_par(par)
        if bar_len:
            self._drum.set_bar_len(bar_len)

    def _update_view(self) -> None:
        self.menu_client_queue([ConfigName.menu_client_redraw, self._di])

    def _menu_client_redraw(self, di: DrawInfo) -> None:
        self._di = di

        di.header = f"{self._drum}"
        if di.update_method:
            # noinspection PyBroadException
            try:
                method = getattr(self, di.update_method)
                di.content = method()
            except Exception as ex:
                MyLog().exception(ex)
                di.content = ""
        part = self._song.get_item()
        di.part_len = part.get_len()
        di.max_loop_len = part.get_max_len(di.part_len)
        di.idx = self.idx
        di.is_rec = self.get_is_rec()
        self.__send_q.put([ConfigName.menu_client_redraw, di])

    # ===============+ other methods ===============================

    def _looper_restart(self) -> None:
        self._song_stop()
        os.system("killall -9 -qw python > /dev/null")

    @staticmethod
    def _menu_config_show() -> str:
        dic = load_ini_section("MENU")
        return "Menu: " + dic.get(ConfigName.menu_dir, "")

    @staticmethod
    def _menu_config_iterate() -> None:
        tmp = load_ini_section("MENU")
        config = tmp.get(ConfigName.menu_dir, "")
        ff = FileFinder(find_path("config/menu"), False, "")
        ff.add_item(config)
        ff.iterate(1)  # next menu
        tmp[ConfigName.menu_dir] = ff.get_item()
        update_ini_section("MENU", tmp)

    @staticmethod
    def _looper_update() -> None:
        os.system("git reset --hard; clear; git pull")
        time.sleep(5)

    @staticmethod
    def _server_start() -> None:
        os.system("python -m http.server 8000")

    #  ============ all parts methods ===============

    def _part_undo(self) -> None:
        part = self._song.get_item()
        if part.item_count() <= 1:
            return

        is_rec = self.get_is_rec()
        self._set_is_rec(False)

        if not is_rec:
            part.undo()
        else:
            part.delete_selected()

    def _part_redo(self) -> None:
        self._set_is_rec(False)
        part = self._song.get_item()
        part.redo()

    # ================= one part methods ====================================

    def _loop_iterate(self, steps: int) -> None:
        self._song.get_item().iterate(steps)

    def _loop_edit(self, action: str) -> None:
        part = self._song.get_item()
        loop = part.get_item()
        if action == "silent":
            loop.set_silent(not loop.is_silent())
        elif action == "reverse":
            loop.flip_reverse()
        elif action == "move" and part != loop:
            deleted = part.delete_selected()
            if deleted:
                part.add_item(deleted)
        elif action == "delete" and part != loop:
            part.delete_selected()
