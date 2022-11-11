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
from utils import ConfigName, MsgProcessor, RedrawScreen, CONFLDR
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
            self.__redraw.loop_len = self.get_item2().length
            self.__redraw.is_rec = self.is_rec
            infodic["redraw"] = self.__redraw

        if "header" in infodic:
            song_name = CONFLDR.get(ConfigName.song_name, "")
            drum_type = CONFLDR.get(ConfigName.drum_type, "")
            infodic["header"] = f"{drum_type}/{song_name}"

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
        now_id = self._file_finder.find_item_id(CONFLDR.get(ConfigName.song_name, ""))
        return self._file_finder.get_list(now_id)

    @staticmethod
    def _change_drum_type(direction) -> None:
        RDRUM.iterate(direction > 0)

    @staticmethod
    def _show_drum_type() -> str:
        now_id = RDRUM.find_item_id(CONFLDR.get(ConfigName.drum_type, ""))
        return RDRUM.get_list(now_id)

    @staticmethod
    def _load_drum_type() -> None:
        RDRUM.load_drum_type()

    def _show_one_part(self) -> str:
        part = self.get_item2()
        loop = part.get_item()
        now_id = part.find_item_id(loop)
        return part.get_list(now_id)

    def _show_all_parts(self) -> str:
        return self.get_list(self.id2)

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
        if self.id == self.id2:
            return
        save_id = self.id
        self._go_id(self.id2)
        self._stop_never()
        self.delete(save_id, save_backup=False)
        self.align_ids()
        self.append(SongPart(self))

    def _duplicate_part(self) -> None:
        if self.id != self.id2:
            return
        part = self.get_item()
        if part.is_empty:
            return

        empty_id = self.find_empty_part_id()
        if empty_id < 0:
            return

        self.delete(empty_id, save_backup=False)
        new_part: SongPart = copy.deepcopy(part)
        new_part.set_ctrl(self)
        self.append(new_part)

    def _undo_part(self) -> None:
        need_save = not self._is_rec
        self._is_rec = False
        part = self.get_item2()
        part.delete(part.item_count - 1, save_backup=need_save)

    def _redo_part(self) -> None:
        self._is_rec = False
        part = self.get_item2()
        part.redo()

    def _redo_all(self) -> None:
        if self.id != self.id2:
            return
        self._is_rec = False
        part = self.get_item2()
        for _ in range(part.undo_count):
            part.redo()

    #  ================= One song part view and related commands

    def _change_loop(self, *params) -> None:
        if self._is_rec:
            self._is_rec = False
        part = self.get_item2()
        if params[0] == "prev":
            part.iterate(False)
        elif params[0] == "next":
            part.iterate(True)
        elif params[0] == "delete":
            part.delete(part.id, save_backup=False)
        elif params[0] == "silent":
            loop = part.get_item()
            loop.flip_silent()
        elif params[0] == "reverse":
            loop = part.get_item()
            loop.flip_reverse()
        elif params[0] == "move" and part.id:
            part.delete(part.id, save_backup=True)
            part.redo()


if __name__ == "__main__":
    pass
