from abc import ABC
from multiprocessing import Queue
from threading import Event, Thread

from control.loopctrl import LoopCtrl
from drum.loopdrum import LoopDrum
from song.loopsimple import LoopSimple
from song.song import Song
from song.songpart import SongPart
from utils.utilconfig import ConfigName


class SongCtrl(LoopCtrl, ABC):
    """added playback thread and Song.
     Song is collection of song parts with related methods"""

    def __init__(self, queue: Queue):
        LoopCtrl.__init__(self, queue)
        self._song: Song = Song(self)
        self.__next_id: int = 0
        self.__play_event: Event = Event()
        Thread(target=self.__play_loop, name="play_loop", daemon=True).start()

    # ================ song part methods

    def _show_loops(self) -> str:
        part = self._song.get_item()
        return part.loops.get_str()

    def _show_parts(self) -> str:
        return self._song.get_str(self.__next_id)

    def __play_loop(self) -> None:
        """runs in a thread, play and record current song part"""
        while True:
            self.__play_event.wait()
            part = self._song.item_from_idx(self.__next_id)
            self.stop_never()
            self._set_is_rec(part.is_empty)
            self._start_rec_idx, self.idx = 0, 0
            self.add_command([ConfigName.client_redraw, None])
            part.play_loop(self)
            if not self.__play_event.is_set():
                self.add_command(["_stop_drum"])

    def _add_song_part(self) -> None:
        selected: int = self._song.get_idx()
        self.__next_id = self._song.idx_from_item(SongPart())
        self._song.item_from_idx(selected)

    def _change_song_part(self, chg: int) -> None:
        self.__next_id += chg
        self.__next_id %= self._song.item_count()

    def _play_song_part(self, pid: int = None) -> None:
        if pid is None:
            pid = self.__next_id

        bar_len = self._drum.get_bar_len()
        if bar_len == 0 and isinstance(self._drum, LoopDrum):
            pid = 0

        if not self.__play_event.is_set():
            self.__next_id = pid
            self.__play_event.set()
            return

        selected: int = self._song.get_idx()
        if selected == pid and self.__next_id != pid:
            self.__next_id = pid
            self.stop_never()
            return

        self.__next_id = pid
        part: SongPart = self._song.get_item()
        if part.is_empty:
            self.stop_at_bound(bar_len)
            return

        if selected == self.__next_id:
            if self.get_is_rec():
                self._set_is_rec(False)
                part.trim_buffer(self)
            else:
                part.loops.idx_from_item(LoopSimple(part.length))
                part.clear_undo()
                self._set_is_rec(True)
        else:
            if self.get_is_rec():
                self._set_is_rec(False)
                part.trim_buffer(self)

            self.stop_at_bound(part.length)

    def _overdub_song_part(self) -> None:
        if self._song.get_idx() != self.__next_id:
            return
        part: SongPart = self._song.get_item()
        if part.is_empty:
            return
        loop: LoopSimple = part.loops.get_item()
        assert part.loops.get_idx() == part.loops.item_count() - 1
        assert not loop.is_empty
        loop.max_buffer()
        self._start_rec_idx = self.idx

    def _delete_song_part(self) -> None:
        selected = self._song.get_idx()
        if self.__next_id == selected:
            return  # can not delete active part
        elif self.__next_id < selected:
            selected -= 1  # selected will be less after deletion

        self._song.item_from_idx(self.__next_id)
        self._song.delete_selected()
        self._song.item_from_idx(selected)
        self.__next_id = selected

    def _clear_song_part(self) -> None:
        selected: int = self._song.get_idx()
        if self.__next_id == selected:
            return  # can not clear active part
        self._song.item_from_idx(self.__next_id).clear()
        self.__next_id = selected
        self.stop_never()
        self._song.item_from_idx(selected)

    def _redo_all(self) -> None:
        if self._song.get_idx() == self.__next_id:
            self._set_is_rec(False)
            part = self._song.get_item()
            while part.redo():
                pass

    def _stop_song(self, wait: int = 0) -> None:
        self._set_is_rec(False)
        self.__play_event.clear()
        self.__next_id = self._song.get_idx()
        bound = self._song.get_item().length if wait else 0
        self.stop_at_bound(bound)
