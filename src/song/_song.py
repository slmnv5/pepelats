import logging
import pickle
from abc import abstractmethod

from buffer import OneLoopCtrl
from drum.basedrum import SimpleDrum
from song._songpart import SongPart
from utils.utilname import generate_name
from utils.utilother import FileFinder, CollectionOwnerExt


class Song(CollectionOwnerExt[SongPart]):
    """Song keeps SongParts as CollectionOwner, can save and load from file"""

    def __init__(self, first: SongPart):
        CollectionOwnerExt.__init__(self, first)
        self._file_finder: FileFinder = FileFinder("save_song", True, ".s")
        self._name: str = ""

    @abstractmethod
    def get_drum(self) -> SimpleDrum:
        pass

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

        self._name = self._file_finder.get_item()
        self._stop_song()
        full_name = self._file_finder.get_full_name()
        with open(full_name, 'rb') as f:
            length, drum_name, load_list = pickle.load(f)

        assert len(load_list) == 4, f"Loading song: wrong number of parts: {full_name}"

        drum = self.get_drum()
        drum.load_drum_name(drum_name)
        drum.prepare_drum(length)

        ctrl = self._get_control()
        load_list = [x if x is not None else SongPart(ctrl) for x in load_list]

        for part in load_list:
            assert type(part) == SongPart
            part.set_ctrl(ctrl)
            self.attach(part)

        self.set_id(0)
        while self.item_count() > 4:
            self.delete()

        self.set_fixed(self.get_first())
        logging.info(f"Loaded song file: {full_name}")

    def _save_song(self) -> None:
        if not self.get_drum().get_length():
            return

        if not self._name:
            self._name = self.__new_song_name()

        self._file_finder.attach(self._name)
        full_name = self._file_finder.get_full_name()
        length: int = self.get_drum().get_length()
        save_list = list()
        self.apply_to_each(lambda x: save_list.append(None if x.is_empty else x), use_undo=False)

        assert len(save_list) == 4, f"Song must have 4 parts: {full_name}"

        with open(full_name, 'wb') as f:
            pickle.dump((length, self.get_drum().get_item(), save_list), f)

        logging.info(f"Saved song file {full_name}")

    def _save_new_song(self):
        self._name = ""
        self._save_song()

    def _delete_song(self) -> None:
        if self._file_finder.get_item() == self._name:
            self._stop_song()
        self._file_finder.delete()

    def __new_song_name(self) -> str:
        return generate_name() + self._file_finder.get_end_with()
