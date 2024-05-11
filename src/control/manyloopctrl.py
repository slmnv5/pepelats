from abc import ABC
from multiprocessing import Queue
from threading import Event, Thread

from buffer.loopctrl import LoopCtrl
from buffer.loopsimple import LoopSimple
from drum.loopdrum import LoopDrum
from song.song import Song
from song.songpart import SongPart
from utils.utilconfig import ConfigName
from utils.utilfactory import create_drum
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class ManyLoopCtrl(LoopCtrl, ABC):
    """added playback thread and Song.
     Song is collection of song parts with related methods"""

    def __init__(self, queue: Queue, drum_type: str):
        dr = create_drum(drum_type)
        dr.load_drum_config()
        LoopCtrl.__init__(self, queue, dr)
        self._song: Song = Song(self)
        self._next_id: int = 0
        self.__play_event: Event = Event()
        Thread(target=self._play_loop, name="play_loop", daemon=True).start()

    # ================ song part methods

    def _show_loops(self) -> str:
        part = self._song.parts.get_item()
        return part.loops.get_str()

    def _show_parts(self) -> str:
        return self._song.parts.get_str(self._next_id)

    def _play_loop(self) -> None:
        """runs in a thread, play and record current song part"""
        while True:
            self.__play_event.wait()
            part = self._song.parts.set_item(self._next_id)
            self.stop_never()
            self._start_rec_idx, self.idx = 0, 0
            self._set_is_rec(part.is_empty)
            self.add_command([ConfigName.client_redraw, None])
            part.play_buffer(self)
            if not self.__play_event.is_set():
                self.add_command(["_stop_drum"])

    def _add_song_part(self) -> None:
        selected = self._song.parts.get_idx()
        self._next_id = self._song.parts.add_item(SongPart())
        self._song.parts.set_item(selected)

    def _change_song_part(self, chg: int) -> None:
        self._next_id += chg
        self._next_id %= self._song.parts.item_count()

    def _play_song_part(self, pid: int = None) -> None:
        if pid is None:
            pid = self._next_id

        bar_len = self._drum.get_bar_len()
        if bar_len == 0 and isinstance(self._drum, LoopDrum):
            pid = 0

        if not self.__play_event.is_set():
            self._next_id = pid
            self.__play_event.set()
            return

        selected: int = self._song.parts.get_idx()
        if selected == pid and self._next_id != pid:
            self._next_id = pid
            self.stop_never()
            return

        self._next_id = pid
        part: SongPart = self._song.parts.get_item()
        if part.is_empty:
            self.stop_at_bound(bar_len)
            return

        if selected == self._next_id:
            if self.get_is_rec():
                self._set_is_rec(False)
                part.trim_buffer(self)
            else:
                part.loops.add_item(LoopSimple(part.length))
                part.clear_undo()
                self._set_is_rec(True)
        else:
            if self.get_is_rec():
                self._set_is_rec(False)
                part.trim_buffer(self)

            self.stop_at_bound(part.length)

    def _overdub_song_part(self) -> None:
        if self._song.parts.get_idx() != self._next_id:
            return
        part: SongPart = self._song.parts.get_item()
        if part.loops.item_count() <= 1:
            return
        loop: LoopSimple = part.loops.get_item()
        assert part.loops.get_idx() == part.loops.item_count() - 1
        assert not loop.is_empty
        assert self.get_is_rec()
        loop.max_buffer()
        self._start_rec_idx = self.idx

    # ========== drum methods
    def _new_song(self, drum_type: str) -> None:
        old_type, bar_len = self._drum.get_class_name(), self._drum.get_bar_len()
        if old_type == drum_type:
            return
        self._stop_song()
        kwargs = {"SongPart": self._song.parts.set_item(0)}
        dr = create_drum(drum_type, **kwargs)
        dr.load_drum_config(None, bar_len)
        self._drum = dr

    def _load_drum_config(self, bar_len: int = None) -> None:
        self._drum.load_drum_config(None, bar_len)

    # ================= song methods

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

    def _stop_song(self, wait: int = 0) -> None:
        self._set_is_rec(False)
        self.__play_event.clear()
        bound = self._song.parts.get_item().length if wait else 0
        self.stop_at_bound(bound)

    def _init_song(self, part_cnt: int = None) -> None:
        self._stop_song()
        self._next_id = 0
        self._song = Song(self)
        parts = self._song.parts
        if part_cnt is not None and part_cnt < 7:
            while parts.item_count() < part_cnt:
                parts.add_item(SongPart())

        kwargs = {"SongPart": self._song.parts.set_item(0)}
        drum_type = self._drum.get_class_name()
        config_name = self._drum.get_config()
        self._drum = create_drum(drum_type, **kwargs)
        self._drum.load_drum_config(config_name, 0)
