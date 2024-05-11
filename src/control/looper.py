from __future__ import annotations

import os
import time
import traceback
from multiprocessing import Queue

from buffer.loopsimple import LoopSimple
from control.manyloopctrl import ManyLoopCtrl
from utils.utilconfig import ConfigName, SD_RATE, MAX_LEN_SECONDS, load_ini_section, find_path, update_ini_section
from utils.utillog import get_my_log
from utils.utilother import DrawInfo, CollectionOwner, FileFinder
from utils.utilportout import MidiOutWrap

my_log = get_my_log(__name__)


class Looper(ManyLoopCtrl):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_q: Queue, send_q: Queue):
        ManyLoopCtrl.__init__(self, recv_q, "EuclidDrum")
        self._send_q = send_q
        self._saved_draw_info = DrawInfo()

    def _redraw(self, draw_info: DrawInfo) -> None:
        if not draw_info:
            draw_info = self._saved_draw_info
        else:
            self._saved_draw_info = draw_info
        dr = self._drum
        draw_info.header = dr.get_drum_header()
        if draw_info.update_method:
            # noinspection PyBroadException
            try:
                method = getattr(self, draw_info.update_method)
                draw_info.content = method()
            except Exception:
                my_log.error(f"Error: {traceback.format_exc()}")
        else:
            draw_info.content = ""
        assert draw_info.content is not None
        length = self._song.parts.get_item().length
        draw_info.loop_seconds = MAX_LEN_SECONDS if self.get_stop_event().is_set() else length / SD_RATE
        draw_info.loop_position = 0 if not length else (self.idx % length) / length
        draw_info.is_rec = self.get_is_rec()
        self._send_q.put([ConfigName.client_redraw, draw_info])

    # ===============+ other methods

    def _restart_looper(self) -> None:
        self._stop_song()
        os.system("killall -9 python")

    def _update_app(self) -> None:
        self._stop_song()
        os.system("git reset --hard")
        os.system("git pull --ff-only; sleep 2")

    @staticmethod
    def _show_menu_config() -> str:
        dic = load_ini_section(find_path(ConfigName.main_ini), "MENU")
        return "Menu: " + dic.get(ConfigName.menu_dir, "")

    @staticmethod
    def _next_menu_config() -> None:
        dic = load_ini_section(find_path(ConfigName.main_ini), "MENU")
        config = dic.get(ConfigName.menu_dir, "")
        ff = FileFinder(find_path("config/menu"), False, "")
        ff.set_idx(config)
        ff.iterate()
        dic[ConfigName.menu_dir] = ff.get_item()
        update_ini_section(find_path(ConfigName.main_ini), "MENU", dic)

    @staticmethod
    def _show_ports() -> None:
        mow = MidiOutWrap()
        os.system("clear")
        print("\n", mow.show())
        time.sleep(10)

    @staticmethod
    def _connect_bt() -> None:
        os.system("$ROOTDIR/connect_bt.sh")
        time.sleep(3)

    #  ============ All song parts view and related commands

    def _delete_song_part(self) -> None:
        selected = self._song.parts.get_idx()
        if self._next_id == selected:
            return  # can not delete active part
        elif self._next_id < selected:
            selected -= 1  # selected will be less after deletion

        self._song.parts.set_item(self._next_id)
        self._song.parts.delete_selected()
        self._song.parts.set_item(selected)
        self._next_id = selected

    def _clear_part(self) -> None:
        selected: int = self._song.parts.get_idx()
        if self._next_id == selected:
            return  # can not clear active part
        part = self._song.parts.set_item(self._next_id)
        self._next_id = selected
        self.stop_never()
        self._song.parts.set_item(selected)
        if not self._drum.play_samples(part):
            return  # loop drum uses this part, can not delete it
        if not part.is_empty:
            part.max_buffer()
            part.loops = CollectionOwner[LoopSimple](part)

    def _undo_part(self) -> None:
        part = self._song.parts.get_item()
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
        part = self._song.parts.get_item()
        part.redo()

    def _redo_all(self) -> None:
        if self._song.parts.get_idx() == self._next_id:
            self._set_is_rec(False)
            part = self._song.parts.get_item()
            while part.redo():
                pass

    #  ================= One song part view and related commands

    def _change_loop(self, *params) -> None:
        loops = self._song.parts.get_item().loops
        loops.iterate(params[0])

    def _edit_loop(self, *params) -> None:
        part = self._song.parts.get_item()
        loop = part.loops.get_item()
        if params[0] == "silent":
            loop.set_silent(not loop.is_silent())
        elif params[0] == "reverse":
            loop.flip_reverse()
        elif params[0] == "move" and part != loop:
            deleted = part.loops.delete_selected()
            if deleted:
                part.loops.set_idx(deleted)
        elif params[0] == "delete" and part != loop:
            part.loops.delete_selected()
