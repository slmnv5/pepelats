import logging
import os
import traceback
# noinspection PyProtectedMember
from multiprocessing.connection import Connection

from control._manyloopctrl import ManyLoopCtrl
from drum.audiodrum import AudioDrum
from drum.basedrum import SimpleDrum
from drum.mididrum import MidiDrum
from song import SongPart
from utils.utilconfig import SD_RATE
from utils.msgprocessor import MsgProcessor
from utils.utilalsa import get_midi_out
from utils.utilother import DrawInfo
from utils.utilport import FakeOutPort


class ExtendedCtrl(ManyLoopCtrl, MsgProcessor):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_conn: Connection, send_conn: Connection):
        self._dr_audi: SimpleDrum = AudioDrum()
        ManyLoopCtrl.__init__(self, self._dr_audi)
        MsgProcessor.__init__(self, recv_conn, send_conn)

        self.__dr_midi: SimpleDrum = self._dr_audi
        midi_out = get_midi_out()
        if not midi_out:
            midi_out = FakeOutPort()

        if midi_out.is_port_open():
            self.__dr_midi = MidiDrum(midi_out)
        else:
            self.__dr_midi = self._dr_audi

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

    def _drum_midi(self) -> None:
        drum = self.get_drum()
        if self.__dr_midi == drum:
            return
        self.__dr_midi.load_drum_name(drum.get_item())
        self.__dr_midi.prepare_drum(drum.get_length())
        self._set_drum(self.__dr_midi)

    def _drum_audio(self) -> None:
        drum = self.get_drum()
        if self._dr_audi == drum:
            return
        self._dr_audi.load_drum_name(drum.get_item())
        self._dr_audi.prepare_drum(drum.get_length())
        self._set_drum(self._dr_audi)

    #  ============ All song parts view and related commands

    def _clear_part(self) -> None:
        if self.get_id() == self.fixed_id():
            return
        part = self.get_item()
        if part.is_empty:
            return
        self.set_item(SongPart(self))
        self.set_id(self.fixed_id())

    def _duplicate_part(self) -> None:
        if self.get_id() != self.fixed_id():
            return
        part = self.get_item()
        if part.is_empty:
            return
        empty = self.find_first(lambda x: x.is_empty)
        if not empty:
            return
        part.apply_to_each(lambda x: empty.attach(x))
        empty.set_id(0)
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
        if self.get_id() != self.fixed_id():
            return
        self.set_is_rec(False)
        part = self.get_fixed()
        while part.redo():
            pass

    #  ================= One song part view and related commands

    def _loop_volume(self, chg_factor: float):
        loop = self.get_fixed().get_item()
        loop.multiply_buff(chg_factor)
        loop._collection_str = ""

    def _change_loop(self, *params) -> None:
        self.get_fixed().iterate(params[0] > 0)

    def _edit_loop(self, *params) -> None:
        part = self.get_fixed()
        if params[0] == "delete":
            part.delete()
        elif params[0] == "silent":
            part.get_item().flip_silent()
        elif params[0] == "reverse":
            part.get_item().flip_reverse()
        elif params[0] == "move" and part.get_id():
            deleted = part.delete()
            if deleted:
                part.attach(deleted)


if __name__ == "__main__":
    pass
