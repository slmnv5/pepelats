import os
import traceback
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from control._manyloopctrl import ManyLoopCtrl
from song import SongPart
from utils.config import SD_RATE, ROOT_DIR
from utils.log import DumbLog
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
                DumbLog.error(f"ExtendedCtrl method: {self.__draw_info.update_method}, error: {traceback.format_exc()}")

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
        self.get_drum().load_drum_name()

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

    @staticmethod
    def _text_screen():
        os.system("echo 'export TEXT_SCREEN=1'>" + ROOT_DIR + "/.env")

    @staticmethod
    def _gui_screen():
        os.system("echo 'export TEXT_SCREEN=0'>" + ROOT_DIR + "/.env")

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

        empty = self.get_id(empty_id)
        part.apply_to_each(lambda x: empty.append(x))
        empty.delete(0)

    def _undo_part(self) -> None:
        save_undo = not self.get_is_rec()
        self.set_is_rec(False)
        part = self.get_fixed()
        part.delete(part.item_count - 1, save_undo)

    def _redo_part(self) -> None:
        self.set_is_rec(False)
        part = self.get_fixed()
        part.redo()

    def _redo_all(self) -> None:
        if self.id != self.fixed_id:
            return
        self.set_is_rec(False)
        part = self.get_fixed()
        for _ in range(part.undo_count):
            part.redo()

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
