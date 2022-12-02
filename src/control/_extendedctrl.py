import traceback
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from control._manyloopctrl import ManyLoopCtrl
from drum.audiodrum import AudioDrum
from song import SongPart
from utils import MsgProcessor
from utils.log import LOGGER
from utils.utilother import run_os_cmd, RedrawScreen


class ExtendedCtrl(ManyLoopCtrl, MsgProcessor):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_conn: Connection, send_conn: Connection):
        ManyLoopCtrl.__init__(self, AudioDrum())
        MsgProcessor.__init__(self, recv_conn, send_conn)

        self.__redraw = RedrawScreen()

    def _redraw(self) -> None:
        self._send_redraw(self.__redraw)

    def _send_redraw(self, redraw) -> None:
        self.__redraw = redraw
        self.__redraw.header = f"{self.get_drum()}/{self._file_finder.get_fixed()}"

        if self.__redraw.update:
            # noinspection PyBroadException
            try:
                method = getattr(self, self.__redraw.update)
                self.__redraw.content = method()
            except Exception:
                LOGGER.error(f"ExtendedCtrl method: {self.__redraw.update}, error: {traceback.format_exc()}")

        self.__redraw.idx = self.idx
        self.__redraw.is_stop = self.get_stop_event().is_set()
        self.__redraw.loop_len = self.get_fixed().length
        self.__redraw.is_rec = self.get_is_rec()

        MsgProcessor._send_redraw(self, self.__redraw)

    # ================ show methods

    def _change_song(self, *params) -> None:
        self._file_finder.iterate(go_fwd=params[0] > 0)

    def _show_song(self) -> str:
        return self._file_finder.get_str()

    def _change_drum_type(self, direction) -> None:
        self.get_drum().iterate(direction > 0)

    def _show_drum_type(self) -> str:
        return self.get_drum().get_str()

    def _load_drum_type(self) -> None:
        self.get_drum().load_drum_type()

    def _show_one_part(self) -> str:
        part = self.get_fixed()
        return part.get_str()

    def _show_all_parts(self) -> str:
        return self.get_str()

    @staticmethod
    def _check_updates() -> None:
        run_os_cmd(["git", "reset", "--hard"])
        run_os_cmd(["git", "pull", "--ff-only"])

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
