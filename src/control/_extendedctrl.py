import logging
import os
import traceback
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from control._manyloopctrl import ManyLoopCtrl
from song import SongPart
from utils.config import SD_RATE
from utils.msgprocessor import MsgProcessor
from utils.utilother import DrawInfo


class ExtendedCtrl(ManyLoopCtrl, MsgProcessor):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_conn: Connection, send_conn: Connection):
        ManyLoopCtrl.__init__(self)
        MsgProcessor.__init__(self, recv_conn, send_conn)

        self.__draw_info = DrawInfo()

    def _redraw(self) -> None:
        self._send_redraw(self.__draw_info)

    def _send_redraw(self, redraw: DrawInfo) -> None:
        self.__draw_info = redraw
        self.__draw_info.header = f"{self.get_drum()}"
        self.__draw_info.content = ""
        if self.__draw_info.update_method:
            # noinspection PyBroadException
            try:
                method = getattr(self, self.__draw_info.update_method)
                self.__draw_info.content = method()
            except Exception:
                logging.error(f"ExtendedCtrl method: {self.__draw_info.update_method}, error: {traceback.format_exc()}")

        length = self.get_fixed().length
        self.__draw_info.loop_seconds = length / SD_RATE
        self.__draw_info.loop_position = (self.idx % length) / length
        self.__draw_info.is_stop = self.get_stop_event().is_set()
        self.__draw_info.is_rec = self.get_is_rec()

        MsgProcessor._send_redraw(self, self.__draw_info)

    # ================ show methods

    def _change_song(self, *params) -> None:
        self._file_finder.iterate(go_fwd=params[0] > 0)

    def _show_song(self) -> str:
        return self._file_finder.get_str()

    def _change_drum_name(self, direction) -> None:
        self.get_drum().iterate(direction > 0)

    def _show_drum_name(self) -> str:
        return self.get_drum().get_str()

    def _load_drum_name(self) -> None:
        drum = self.get_drum()
        drum.load_drum_name(drum.get_item())
        drum.prepare_drum(drum.get_length())

    def _show_one_part(self) -> str:
        part = self.get_fixed()
        return part.get_str()

    def _show_all_parts(self) -> str:
        return self.get_str()

    @staticmethod
    def _sleep_sec(sec: int) -> None:
        os.system(f"timeout {sec}")
        os.system(f"sleep {sec}")

    @staticmethod
    def _check_updates() -> None:
        os.system("git reset --hard")
        os.system("git pull --ff-only")

    def _drum_kind(self):
        self.change_drum_kind()

    #  ============ All song parts view and related commands

    def _clear_part(self) -> None:
        if self.id == self.fixed_id:
            return
        part = self.get_item()
        if part.is_empty:
            return
        self.set_item(SongPart(self))
        self.go_id(self.fixed_id)

    def _duplicate_part(self) -> None:
        if self.id != self.fixed_id:
            return
        part = self.get_item()
        if part.is_empty:
            return
        empty = self.find_first(lambda x: x.is_empty)
        if not empty:
            return
        part.apply_to_each(lambda x: empty.attach(x))
        empty.go_id(0)
        empty.delete()

    def _undo_part(self) -> None:
        was_rec = self.get_is_rec()
        self.set_is_rec(False)
        part = self.get_fixed()
        if not was_rec:
            part.undo()
        else:
            part.delete()

    def _redo_part(self) -> None:
        self.set_is_rec(False)
        part = self.get_fixed()
        part.redo()

    def _redo_all(self) -> None:
        if self.id != self.fixed_id:
            return
        self.set_is_rec(False)
        part = self.get_fixed()
        while part.redo():
            pass

    #  ================= One song part view and related commands

    def _change_loop(self, *params) -> None:
        if self.get_is_rec():
            self.set_is_rec(False)

        part = self.get_fixed()
        if params[0] == "prev":
            part.iterate(False)
        elif params[0] == "next":
            part.iterate(True)
        elif params[0] == "delete":
            part.delete()
        elif params[0] == "silent":
            loop = part.get_item()
            loop.flip_silent()
        elif params[0] == "reverse":
            loop = part.get_item()
            loop.flip_reverse()
        elif params[0] == "move" and part.id:
            deleted = part.delete()
            if deleted:
                part.attach(deleted)


if __name__ == "__main__":
    pass
