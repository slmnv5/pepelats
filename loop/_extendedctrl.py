import copy
import os
import traceback
# noinspection PyProtectedMember
from multiprocessing.connection import Connection
from typing import Dict

from drum import RDRUM
from utils import LOGR
from loop._manyloopctrl import ManyLoopCtrl
from loop._songpart import SongPart
from mixer import Mixer
from utils import MsgProcessor, RedrawScreen
from utils import run_os_cmd


class ExtendedCtrl(ManyLoopCtrl, MsgProcessor):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_conn: Connection, send_conn: Connection):
        ManyLoopCtrl.__init__(self)
        MsgProcessor.__init__(self, recv_conn, send_conn)
        self.__redraw = RedrawScreen("", "", 0, 0, True, False)
        self.__mixer: Mixer = Mixer()

    def _redraw(self) -> None:
        self._send_redraw({"redraw": 0})

    def _send_redraw(self, infodic: Dict) -> None:
        if "update_method" in infodic:
            self.__redraw.update_method = infodic["update_method"]

        if "redraw" in infodic:
            self.__redraw.content = ""
            if self.__redraw.update_method:
                # noinspection PyBroadException
                try:
                    method = getattr(self, self.__redraw.update_method)
                    self.__redraw.content = method()
                except Exception:
                    LOGR.error(f"ExtendedCtrl method: {self.__redraw.update_method}, error: {traceback.format_exc()}")

            self.__redraw.idx = self.idx
            self.__redraw.is_stop = self.get_stop_event().is_set()
            self.__redraw.loop_len = self.get_part().length
            self.__redraw.is_rec = self.is_rec
            infodic["redraw"] = self.__redraw

        if "header" in infodic:
            infodic["header"] = f"{RDRUM.get_item()}/{self._file_finder.get_item()}"

        MsgProcessor._send_redraw(self, infodic)

    #  ========= change methods for mixer

    def _change_mixer_in(self, change_by: int) -> None:
        self.__mixer.change_volume(change_by, out=False)

    def _change_mixer_out(self, change_by: int) -> None:
        self.__mixer.change_volume(change_by, out=True)

    # ================ show methods

    def _change_song(self, *params) -> None:
        self._file_finder.iterate(go_fwd=params[0] > 0)

    def _show_song(self) -> str:
        return self._file_finder.get_list()

    @staticmethod
    def _change_drum_type(direction) -> None:
        RDRUM.iterate(direction > 0)

    @staticmethod
    def _show_drum_type() -> str:
        return RDRUM.get_list()

    @staticmethod
    def _load_drum_type() -> None:
        RDRUM.load_drum_type()

    def _show_one_part(self) -> str:
        part = self.get_part()
        return part.get_list()

    def _show_all_parts(self) -> str:
        return self.get_list(self.part_id)

    def _show_mixer_volume(self) -> str:
        return f"Mixer volume\noutput:{self.__mixer.getvolume(out=True):.2F}\n" \
               f"input:{self.__mixer.getvolume(out=False):.2F}"

    # ================ other methods

    def _fade_and_stop(self, seconds: int) -> None:
        self._go_play.clear()
        self.__mixer.fade(seconds)
        self.stop_at_bound(0)

    @staticmethod
    def _restart() -> None:
        if os.name == "posix":
            run_os_cmd(["killall", "-9", "python"])
        else:
            run_os_cmd(["taskkill", "/F", "/IM", "python.exe"])

    @staticmethod
    def _check_updates() -> None:
        run_os_cmd(["git", "reset", "--hard"])
        if 0 == run_os_cmd(["git", "pull", "--ff-only"]):
            ExtendedCtrl._restart()

    #  ============ All song parts view and related commands

    def _clear_part(self) -> None:
        if self.id == self.part_id:
            return
        save_id = self.id
        self.go_id(self.part_id)
        self._stop_never()
        self.delete(save_id)
        self.align_ids()
        self.append(SongPart(self))

    def _duplicate_part(self) -> None:
        if self.id != self.part_id:
            return
        part = self.get_item()
        if part.is_empty:
            return

        empty_id = self.first_id(lambda x: self.get_id(x).is_empty, -1)
        if empty_id < 0:
            return

        self.delete(empty_id)
        new_part: SongPart = copy.deepcopy(part)
        new_part.set_ctrl(self)
        self.append(new_part)

    def _undo_part(self) -> None:
        need_save = not self._is_rec
        self._is_rec = False
        part = self.get_part()
        deleted = part.delete(part.item_count - 1)
        if need_save:
            part.append_undo(deleted)

    def _redo_part(self) -> None:
        self._is_rec = False
        part = self.get_part()
        part.redo()

    def _redo_all(self) -> None:
        if self.id != self.part_id:
            return
        self._is_rec = False
        part = self.get_part()
        for _ in range(part.undo_count):
            part.redo()

    #  ================= One song part view and related commands

    def _change_loop(self, *params) -> None:
        if self._is_rec:
            self._is_rec = False
        part = self.get_part()
        if params[0] == "prev":
            part.iterate(False)
        elif params[0] == "next":
            part.iterate(True)
        elif params[0] == "delete":
            part.delete(part.id)
        elif params[0] == "silent":
            loop = part.get_item()
            loop.flip_silent()
        elif params[0] == "reverse":
            loop = part.get_item()
            loop.flip_reverse()
        elif params[0] == "move" and part.id:
            deleted = part.delete(part.id)
            part.append(deleted)


if __name__ == "__main__":
    pass
