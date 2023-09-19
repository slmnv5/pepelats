from __future__ import annotations

import os
import time
import traceback
from multiprocessing import Queue

from buffer.loopsimple import LoopSimple
from control.manyloopctrl import ManyLoopCtrl
from mvc.menuclient import MenuClient
from utils.utilconfig import ConfigName, SD_RATE, MAX_LEN_SECONDS
from utils.utillog import get_my_log
from utils.utilother import DrawInfo, CollectionOwner
from utils.utilportout import MidiOutWrap

my_log = get_my_log(__name__)


class Looper(ManyLoopCtrl, MenuClient):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_q: Queue, send_q: Queue):
        ManyLoopCtrl.__init__(self)
        MenuClient.__init__(self, recv_q)
        self._send_q = send_q
        self._saved_draw_info = DrawInfo()

    def _redraw(self, draw_info: DrawInfo) -> None:
        if not draw_info:
            draw_info = self._saved_draw_info
        else:
            self._saved_draw_info = draw_info
        dr = self._drum
        draw_info.header = f"{dr.get_config()[:-4]}-{dr.get_bpm():05.2F}-{dr}"
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
        length = self._song.parts.selected_item().length
        draw_info.loop_seconds = MAX_LEN_SECONDS if self.get_stop_event().is_set() else length / SD_RATE
        draw_info.loop_position = 0 if not length else (self.idx % length) / length
        draw_info.is_rec = self.get_is_rec()
        self._send_q.put([ConfigName.client_redraw, draw_info])

    # ===============+ other methods
    def _gui_test(self):
        self._send_q.put(["_gui_test"])

    def _restart_looper(self) -> None:
        self._stop_song()
        os.system("killall -9 python")

    def _update_app(self) -> None:
        self._stop_song()
        os.system("git reset --hard")
        os.system("git pull --ff-only; sleep 2")

    @staticmethod
    def _show_ports() -> None:
        mow = MidiOutWrap()
        print(mow.show())
        time.sleep(10)

    #  ============ All song parts view and related commands

    def _clear_part(self, pid: int) -> None:
        selected = self._song.parts.selected_idx()
        if pid == selected:
            return  # can not delete active part
        part = self._song.parts.select_idx(pid)
        self._next_id = selected
        self._song.parts.select_idx(selected)
        if id(part) == self._drum.get_id():
            return  # loop drum uses part, can not delete it
        if part.is_empty:
            return

        self.stop_never()
        part.new_buff()
        part.loops = CollectionOwner[LoopSimple](part)

    def _undo_part(self) -> None:
        is_rec = self.get_is_rec()
        self._set_is_rec(False)
        part = self._song.parts.selected_item()
        if not is_rec:
            part.undo()
        else:
            part.loops.delete_selected()

    def _redo_part(self) -> None:
        self._set_is_rec(False)
        part = self._song.parts.selected_item()
        part.redo()

    def _redo_all(self) -> None:
        if self._song.parts.selected_idx() == self._next_id:
            self._set_is_rec(False)
            part = self._song.parts.selected_item()
            while part.redo():
                pass

    #  ================= One song part view and related commands

    def _change_loop_volume(self, chg_factor: float):
        loop = self._song.parts.selected_item().loops.selected_item()
        loop.multiply_buff(chg_factor)
        loop._collection_str = ""

    def _change_loop(self, *params) -> None:
        self._song.parts.selected_item().loops.iterate(params[0])

    def _edit_loop(self, *params) -> None:
        part = self._song.parts.selected_item()
        loop = part.loops.selected_item()
        if params[0] == "silent":
            loop.flip_silent()
        elif params[0] == "reverse":
            loop.flip_reverse()
        elif params[0] == "move" and part != loop:
            deleted = part.loops.delete_selected()
            if deleted:
                part.loops.add_item(deleted)
        elif params[0] == "delete" and part != loop:
            part.loops.delete_selected()

    # =========== MIDI
