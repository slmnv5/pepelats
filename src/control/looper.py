import os
import time
from multiprocessing import Queue

from control.songctrl import SongCtrl
from utils.utilconfig import ConfigName, load_ini_section, find_path, update_ini_section, SD_RATE
from utils.utillog import MYLOG
from basic.midiinfo import show_out_ports
from utils.utilother import DrawInfo, FileFinder


class Looper(SongCtrl):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_q: Queue, send_q: Queue):
        SongCtrl.__init__(self, recv_q, "LoopDrum")
        self._send_q = send_q
        self._saved_draw_info = DrawInfo()

    def _menu_client_redraw(self, draw_info: DrawInfo) -> None:
        if not draw_info:
            draw_info = self._saved_draw_info
        else:
            self._saved_draw_info = draw_info

        draw_info.header = self._drum_type if not self._drum.get_bar_len() else f"{self._drum}"
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
        length = self._song.get_item().length
        draw_info.loop_seconds = length / SD_RATE
        draw_info.loop_position = (self.idx % length) / length
        draw_info.is_rec = self.get_is_rec()
        self._send_q.put([ConfigName.menu_client_redraw, draw_info])

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
    def _show_midi_out_ports() -> None:
        os.system("clear")
        print("\n", show_out_ports())
        time.sleep(10)

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
