import pickle
from abc import abstractmethod
from time import sleep

from drum import RDRUM
from loop._oneloopctrl import OneLoopCtrl
from loop._songpart import SongPart
from utils import FileFinder, CollectionOwner
import logging
from utils import generate_name


class Song(CollectionOwner[SongPart]):
    """Song keeps SongParts as CollectionOwner, can save and load from file"""

    def __init__(self, first: SongPart):
        CollectionOwner.__init__(self, first)
        self._file_finder: FileFinder = FileFinder("save_song", True, ".s")

    def get_part(self) -> SongPart:
        return self.get_fixed()

    def align_ids(self) -> None:
        self.set_fixed(self.get_item())

    @abstractmethod
    def _stop_song(self, wait: int = 0) -> None:
        pass

    @abstractmethod
    def _init_song(self) -> None:
        pass

    @abstractmethod
    def _get_control(self) -> OneLoopCtrl:
        pass

    def _load_song(self) -> None:
        if not self._file_finder.get_item():
            return
        self._stop_song()
        full_name = self._file_finder.get_full_name()
        with open(full_name, 'rb') as f:
            length, drum_type, load_list = pickle.load(f)

        assert length > 0, f"Loading song: length <= 0: {full_name}"
        assert len(load_list) == 4, f"Loading song: wrong number of parts: {full_name}"

        RDRUM.set_fixed(drum_type)
        RDRUM.load_drum_type()
        RDRUM.prepare_drum(length)

        ctrl = self._get_control()
        load_list = [x if x is not None else SongPart(ctrl) for x in load_list]

        for part in load_list:
            assert type(part) == SongPart
            part.set_ctrl(ctrl)
            self.append(part)

        while self.item_count > 4:
            self.delete(0)

        self._file_finder.set_fixed(self._file_finder.get_item())
        self.go_id(0)
        self.align_ids()
        while not RDRUM.get_length():
            sleep(0.1)

        logging.info(f"Loaded song file: {full_name}")

    def _save_song(self) -> None:
        if not self._file_finder.get_fixed():
            return

        self._file_finder.go_fixed()
        full_name = self._file_finder.get_full_name()
        length: int = RDRUM.get_length()
        save_list = list()
        self.apply_to_each(lambda x: save_list.append(None if x.is_empty else x), use_undo=False)

        assert len(save_list) == 4, f"Song must have 4 parts: {full_name}"

        with open(full_name, 'wb') as f:
            pickle.dump((length, RDRUM.get_item(), save_list), f)

        logging.info(f"Saved song file {full_name}")

    def _save_new_song(self):
        tmp = self.__new_song_name()
        self._file_finder.set_fixed(tmp)
        self._save_song()

    def _delete_song(self) -> None:
        del_playing = self._file_finder.id == self._file_finder.fixed_id
        self._file_finder.delete(self._file_finder.id)
        self._file_finder.iterate(True)
        if del_playing:
            self._load_song()

    def __new_song_name(self) -> str:
        return generate_name() + self._file_finder.get_end_with()
