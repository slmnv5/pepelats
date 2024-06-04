from abc import ABC
from multiprocessing import Queue
from threading import Event, Thread

from control.loopctrl import LoopCtrl
from drum.basedrum import BaseDrum
from drum.drumfactory import create_drum
from song.loopsimple import LoopSimple
from song.song import Song
from song.songpart import SongPart
from utils.utilconfig import ConfigName


class SongCtrl(LoopCtrl, ABC):
    """added playback thread and Song.
     Song is collection of song parts with related methods"""

    def __init__(self, queue: Queue, drum_type: str, load_song: bool = False):
        LoopCtrl.__init__(self, queue, drum_type)
        self._song: Song = Song(self, load_song)
        self.__next_id: int = 0
        self.__play_event: Event = Event()
        self._start_rec: bool = False  # if start non-empty loop with recording
        Thread(target=self.__play_loop, name="play_loop", daemon=True).start()

    def _drum_create(self, bar_len: int, drum_type: str = None, drum_info: dict[str, any] = None) -> None:
        if drum_type:
            self._drum_type = drum_type

        if drum_info is None:
            drum_info = dict()

        if self._drum_type == ConfigName.LoopDrum:
            drum_info[ConfigName.drum_song_part] = self._song.get_at_idx(0)

        self._drum = create_drum(bar_len, self._drum_type, **drum_info)

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
            self._song.select_idx(self.__next_id)
            part = self._song.get_item()
            self.stop_never()
            self._set_is_rec(part.is_empty or self._start_rec)
            self._start_rec_idx, self.idx = 0, 0
            self.menu_client_queue([ConfigName.menu_client_redraw, None])
            part.play_loop(self)
            if not self.__play_event.is_set():
                self.menu_client_queue(["_drum_stop"])

    def _add_song_part(self) -> None:
        selected: int = self._song.get_idx()
        self.__next_id = self._song.idx_from_item(SongPart())
        self._song.select_idx(selected)

    def _change_song_part(self, chg: int) -> None:
        self.__next_id += chg
        self.__next_id %= self._song.item_count()

    def _play_song_part(self, pid: int = None) -> None:
        self._start_rec = False
        if pid is None:
            pid = self.__next_id

        changed_pid: bool = pid != self.__next_id  # did next_id change form prev. call
        self.__next_id = pid

        if not self.__play_event.is_set():  # not playing now
            self.__play_event.set()
            return

        selected: int = self._song.get_idx()
        part: SongPart = self._song.get_item()
        if part.is_empty:  # empty part, stop ASAP
            self.stop_at_bound(self._drum.get_bar_len())
            return

        if selected == self.__next_id:  # already playing this part
            if changed_pid:  # just changed our mind, returned back to selected
                self.stop_never()
                return
            else:  # we call with same pid 2nd time
                if self.get_is_rec():
                    self._set_is_rec(False)
                    part.trim_buffer(self)
                else:
                    part.loops.idx_from_item(LoopSimple(part.length))
                    part.clear_undo()
                    self._set_is_rec(True)
        else:  # asked to play another part
            if self.get_is_rec():
                self._set_is_rec(False)
                part.trim_buffer(self)

            self.stop_at_bound(part.length)

    def _overdub_song_part(self) -> None:
        if self._song.get_idx() != self.__next_id:
            self._start_rec = True
            return
        part: SongPart = self._song.get_item()
        if part.is_empty:
            return
        loops = part.loops
        k = loops.get_idx()
        if self.get_is_rec() and k > 0:
            loops.set_at_idx(k, LoopSimple())
            self._start_rec_idx = self.idx

    def _delete_song_part(self) -> None:
        selected = self._song.get_idx()
        if self.__next_id == selected:
            return  # can not delete active part
        elif self.__next_id < selected:
            selected -= 1  # selected will be less after deletion

        self._song.select_idx(self.__next_id)
        self._song.delete_selected()
        self._song.select_idx(selected)
        self.__next_id = selected

    def _clear_song_part(self) -> None:
        selected: int = self._song.get_idx()
        if self.__next_id == selected:
            return  # can not clear active part
        self._song.set_at_idx(self.__next_id, SongPart())
        self.__next_id = selected
        self.stop_never()

    def _redo_all(self) -> None:
        if self._song.get_idx() == self.__next_id:
            self._set_is_rec(False)
            part = self._song.get_item()
            while part.redo():
                pass

        # ================= song methods =============================

    def _song_delete(self) -> None:
        self._song_stop()
        self._song.delete_song()

    def _song_load(self) -> None:
        self._song_stop()
        self._song.load_song()

    def _song_save(self) -> None:
        self._song_stop()
        self._song.save_song()

    def _song_name(self) -> str:
        return self._song.get_complete_name()

    def _song_list(self) -> str:
        return self._song.show_songs()

    def _song_iterate(self, steps: int) -> None:
        self._song.iterate_song(steps)

    def _song_new(self, drum_type: str = "") -> None:
        self._drum.stop()
        self._song_stop()
        if not drum_type:
            self._song.clear()
            self._drum = BaseDrum()
            return
        if drum_type != self._drum_type:
            self._drum_type = drum_type
            bar_len = self._drum.get_bar_len()
            if bar_len:
                self._drum_create(bar_len)

    def _song_stop(self, wait: int = 0) -> None:
        self._set_is_rec(False)
        self.__play_event.clear()
        self.__next_id = self._song.get_idx()
        bound = self._song.get_item().length if wait else 0
        self.stop_at_bound(bound)
