import os
import time
from multiprocessing import Queue

from control.songctrl import SongCtrl
from drum.bufferdrum import EuclidDrum, StyleDrum
from drum.loopdrum import LoopDrum
from drum.mididrum import MidiDrum
from mvc.menuclient import MenuClient
from utils.utilconfig import ConfigName
from utils.utilconfig import load_ini_section, find_path, update_ini_section, SD_RATE
from utils.utillog import MYLOG
from utils.utilother import DrawInfo, FileFinder


class Looper(MenuClient, SongCtrl):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_q: Queue, send_q: Queue, drum_type: str):
        MenuClient.__init__(self, recv_q)
        SongCtrl.__init__(self, drum_type)
        self.__send_q = send_q

    def drum_create(self, bar_len: int, **kwargs) -> None:
        drum_type: str = kwargs.get(ConfigName.drum_type, ConfigName.StyleDrum)
        if drum_type == ConfigName.EuclidDrum:
            drum = EuclidDrum()
        elif drum_type == ConfigName.StyleDrum:
            drum = StyleDrum()
        elif drum_type == ConfigName.MidiDrum:
            drum = MidiDrum()
        elif drum_type == ConfigName.LoopDrum:
            drum = LoopDrum(kwargs.get(ConfigName.drum_song_part))
        else:
            raise RuntimeError(f"Unknown drum type: {drum_type}")

        config: str = kwargs.get(ConfigName.drum_config)
        drum.set_config(config)

        volume: float = kwargs.get(ConfigName.drum_volume)
        if volume:
            drum.set_volume(volume)
        par: float = kwargs.get(ConfigName.drum_par)
        if par:
            drum.set_par(par)

        drum.set_bar_len(bar_len)
        drum.randomize()

    def _update_view(self) -> None:
        self.menu_client_queue([ConfigName.menu_client_redraw, self._di])

    def _menu_client_redraw(self, draw_info: DrawInfo) -> None:
        self._di = draw_info

        draw_info.header = f"{self._drum}"
        if draw_info.update_method:
            # noinspection PyBroadException
            try:
                method = getattr(self, draw_info.update_method)
                draw_info.content = method()
            except Exception as ex:
                MYLOG.exception(ex)
        else:
            draw_info.content = ""
        assert draw_info.content is not None
        part = self._song.get_item()
        length1: int = part.get_len()
        draw_info.loop_seconds = length1 / SD_RATE
        draw_info.loop_position = (self.idx % length1) / length1
        length2 = part.get_max_len()
        draw_info.max_loop_position = (self.idx % length2) / length2
        draw_info.max_loop_factor = length2 / length1
        draw_info.is_rec = self.get_is_rec()
        self.__send_q.put([ConfigName.menu_client_redraw, draw_info])

    # ===============+ other methods ===============================

    def _restart_looper(self) -> None:
        self._song_stop()
        os.system("killall -9 python")

    def _update_app(self) -> None:
        self._song_stop()
        os.system("git reset --hard")
        os.system("git pull --ff-only; sleep 2")

    @staticmethod
    def _show_menu_config() -> str:
        dic = load_ini_section("MENU")
        return "Menu: " + dic.get(ConfigName.menu_dir, "")

    @staticmethod
    def _next_menu_config() -> None:
        tmp = load_ini_section("MENU")
        config = tmp.get(ConfigName.menu_dir, "")
        ff = FileFinder(find_path("config/menu"), False, "")
        ff.idx_from_item(config)
        ff.iterate()  # next menu
        tmp[ConfigName.menu_dir] = ff.get_item()
        update_ini_section("MENU", tmp)

    @staticmethod
    def _update() -> None:
        os.system("git reset --hard; clear; git pull")
        time.sleep(5)

    #  ============ all parts methods ===============

    def _undo_part(self) -> None:
        part = self._song.get_item()
        if part.loops.item_count() <= 1:
            return

        is_rec = self.get_is_rec()
        self._set_is_rec(False)

        if not is_rec:
            part.undo()
        else:
            part.loops.delete_selected()

    def _redo_part(self) -> None:
        self._set_is_rec(False)
        part = self._song.get_item()
        part.redo()

    # ================= one part methods ====================================

    def _change_loop(self, *params) -> None:
        loops = self._song.get_item().loops
        loops.iterate(params[0])

    def _edit_loop(self, *params) -> None:
        part = self._song.get_item()
        loop = part.loops.get_item()
        if params[0] == "silent":
            loop.set_silent(not loop.is_silent())
        elif params[0] == "reverse":
            loop.flip_reverse()
        elif params[0] == "move" and part != loop:
            deleted = part.loops.delete_selected()
            if deleted:
                part.loops.idx_from_item(deleted)
        elif params[0] == "delete" and part != loop:
            part.loops.delete_selected()
