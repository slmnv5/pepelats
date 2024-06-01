from abc import ABC
from multiprocessing import Queue
from threading import Event, Thread
from time import sleep

from control.loopctrl import LoopCtrl
from drum.drumfactory import DrumFactory
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
        Thread(target=self.__play_loop, name="play_loop", daemon=True).start()

    def _drum_create(self, bar_len: int, drum_type: str = None, drum_info: dict[str, any] = None) -> None:
        if drum_type:
            self._drum_type = drum_type

        if drum_info is None:
            drum_info = dict()

        if self._drum_type == ConfigName.LoopDrum:
            drum_info[ConfigName.drum_songpart] = self._song.item_from_idx(0)

        drum = DrumFactory.create_drum(bar_len, self._drum_type, **drum_info)
        self.set_drum(drum)

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
            self._set_is_rec(part.is_empty)
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
            self.stop_at_bound(self.drum.get_bar_len())
            return

        if selected == self.__next_id:  # already plaing this part
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

        self._song.select_idx(self.__next_id)
        self._song.delete_selected()
        self._song.select_idx(selected)
        self.__next_id = selected

    def _clear_song_part(self) -> None:
        selected: int = self._song.get_idx()
        if self.__next_id == selected:
            return  # can not clear active part
        self._song.select_idx(self.__next_id)
        self._song.get_item().clear()
        self.__next_id = selected
        self.stop_never()
        self._song.select_idx(selected)

    def _redo_all(self) -> None:
        if self._song.get_idx() == self.__next_id:
            self._set_is_rec(False)
            part = self._song.get_item()
            while part.redo():
                pass

        # ================= song methods =============================

    def _song_init(self) -> None:
        self.drum.stop()
        self._song_stop()
        self.set_drum(None)
        self._song.clear()

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

    def _song_new(self, drum_type: str) -> None:
        self._song_stop()
        sleep(2)
        self._drum_type = drum_type
        self._song.clear()
        self.set_drum(None)

    def _song_stop(self, wait: int = 0) -> None:
        self._set_is_rec(False)
        self.__play_event.clear()
        self.__next_id = self._song.get_idx()
        bound = self._song.get_item().length if wait else 0
        self.stop_at_bound(bound)
