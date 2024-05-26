from __future__ import annotations

import os
import time
import traceback
from multiprocessing import Queue

from control.manyloopctrl import ManyLoopCtrl
from drum.drumfactory import DrumFactory
from song.song import Song
from song.songpart import SongPart
from utils.utilaudio import SD_RATE
from utils.utilconfig import ConfigName, load_ini_section, find_path, update_ini_section
from utils.utillog import MyLog
from utils.utilother import DrawInfo, FileFinder
from utils.utilportout import MidiOutWrap

my_log = MyLog()


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

        draw_info.header = self._drum.get_header()
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
        length = self._song.get_item().length
        draw_info.loop_seconds = length / SD_RATE
        draw_info.loop_position = 0 if not length else (self.idx % length) / length
        draw_info.is_rec = self.get_is_rec()
        self._send_q.put([ConfigName.client_redraw, draw_info])

    # ===============+ other methods ===============================

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
        ff.idx_from_item(config)
        ff.iterate()
        dic[ConfigName.menu_dir] = ff.get_item()
        update_ini_section(find_path(ConfigName.main_ini), "MENU", dic)

    @staticmethod
    def _show_midi_out_ports() -> None:
        mow = MidiOutWrap()
        os.system("clear")
        print("\n", mow.show())
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

    # ================= song methods =============================

    def _init_song(self) -> None:
        self._drum.stop()
        self._stop_song()
        tmp = [SongPart(), SongPart(), SongPart(), SongPart()]
        self._song = Song(tmp)
        kwargs = {"SongPart": self._song.item_from_idx(0)}
        drum_type = self._drum.get_class_name()
        config = self._drum.get_config()
        self._drum = DrumFactory.create_drum(drum_type, **kwargs)
        self._drum.set_config(config)

    def _delete_song(self) -> None:
        self._stop_song()
        self._song.delete_song()

    def _load_song(self) -> None:
        self._stop_song()
        self._song.load_song(self)

    def _save_song(self) -> None:
        self._stop_song()
        self._song.save_song(self)

    def _save_new_song(self) -> None:
        self._stop_song()
        self._song.save_new_song(self)

    def _show_name(self) -> str:
        return self._song.get_complete_name(self)

    def _show_songs(self) -> str:
        return self._song.show_songs()

    def _iterate_song(self, steps: int) -> None:
        self._song.iterate_song(steps)

    # ========== drum methods ==================================
    def _change_drum_type(self, drum_type: str) -> None:
        old_type, bar_len = self._drum.get_class_name(), self._drum.get_bar_len()
        if old_type == drum_type:
            return
        self._stop_song()
        kwargs = {"SongPart": self._song.item_from_idx(0)}
        self._drum = DrumFactory.create_drum(drum_type, **kwargs)
        self._drum.set_config()
        self._drum.set_bar_len(bar_len)

    def _load_drum_config(self) -> None:
        self._drum.set_config()
        bar_len = self._drum.get_bar_len()
        if bar_len:
            self._drum.set_bar_len(bar_len)

    def _init_drum(self, bar_len: int) -> None:
        self._drum.set_bar_len(bar_len)
