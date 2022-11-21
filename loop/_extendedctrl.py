import copy
import logging
import os
import traceback
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from drum import MidiDrum, RealDrum
from loop._loopsimple import LoopSimple
from loop._manyloopctrl import ManyLoopCtrl
from loop._songpart import SongPart
from utils import MsgProcessor, RedrawScreen
from utils import run_os_cmd


class ExtendedCtrl(ManyLoopCtrl, MsgProcessor):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_conn: Connection, send_conn: Connection):
        ManyLoopCtrl.__init__(self, RealDrum())
        MsgProcessor.__init__(self, recv_conn, send_conn)
        self.__redraw = RedrawScreen()

    def _redraw(self) -> None:
        self._send_redraw(self.__redraw)

    def _send_redraw(self, redraw) -> None:
        self.__redraw = redraw
        self.__redraw.header = f"{self.get_drum().get_fixed()}/{self._file_finder.get_fixed()}"

        if self.__redraw.update:
            # noinspection PyBroadException
            try:
                method = getattr(self, self.__redraw.update)
                self.__redraw.content = method()
            except Exception:
                logging.error(f"ExtendedCtrl method: {self.__redraw.update},"
                              f" error: {traceback.format_exc()}")

        self.__redraw.idx = self.idx
        self.__redraw.is_stop = self.get_stop_event().is_set()
        self.__redraw.loop_len = self.get_part().length
        self.__redraw.is_rec = self.is_rec

        MsgProcessor._send_redraw(self, self.__redraw)

    # ================ show methods

    def _change_song(self, *params) -> None:
        self._file_finder.iterate(go_fwd=params[0] > 0)

    def _show_song(self) -> str:
        return self._file_finder.get_str()

    def _change_drum_type(self, direction) -> None:
        self.get_drum().iterate(direction > 0)

    def _change_drum_nature(self) -> None:
        save_len = self.get_drum().get_length()
        is_midi = type(self.get_drum()) == MidiDrum
        drum = RealDrum() if is_midi else MidiDrum()
        self.set_drum(drum)
        if save_len:
            self.get_drum().prepare_drum(save_len)

    def _show_drum_type(self) -> str:
        return self.get_drum().get_str()

    def _load_drum_type(self) -> None:
        self.get_drum().load_drum_type()

    def _show_one_part(self) -> str:
        part = self.get_part()
        return part.get_str()

    def _show_all_parts(self) -> str:
        return self.get_str()

    # ================ other methods

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
        if self.id == self.fixed_id:
            return
        part = self.get_item()
        part.append(LoopSimple(self))
        while part.item_count > 1:
            part.delete(0)
        self.go_fixed()

    def _duplicate_part(self) -> None:
        if self.id != self.fixed_id:
            return
        part = self.get_item()
        if part.is_empty:
            return

        empty_id = self.find_first_id(lambda x: self.get_id(x).is_empty)
        if empty_id < 0:
            return

        self.delete(empty_id)
        new_part: SongPart = copy.deepcopy(part)
        new_part.set_ctrl(self)
        self.append(new_part)

    def _undo_part(self) -> None:
        save_undo = not self._is_rec
        self._is_rec = False
        part = self.get_part()
        part.delete(part.item_count - 1, save_undo)

    def _redo_part(self) -> None:
        self._is_rec = False
        part = self.get_part()
        part.redo()

    def _redo_all(self) -> None:
        if self.id != self.fixed_id:
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
