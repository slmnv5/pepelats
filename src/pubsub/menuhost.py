from abc import ABC
from multiprocessing import Queue

from pubsub.menuloader import MenuLoader
from pubsub.pub import Pub
from utils.util_config import convert_param
from utils.util_log import MY_LOG
from utils.util_menu import NOTE_LETTER
from utils.util_name import AppName


class MenuHost(Pub, MenuLoader, ABC):
    """Translate notes to menu command and put into queue """

    def __init__(self, queue: Queue):
        Pub.__init__(self, queue)
        MenuLoader.__init__(self)
        self.__dic: dict = dict()
        self._menu_update(AppName.play_section)
        self._send_msg([AppName.client_redraw, self.__dic])

    def _menu_update(self, fname: str) -> None:
        super()._menu_update(fname)
        self.__dic[AppName.description] = self.get_command(AppName.description)
        self.__dic[AppName.content] = self.get_command(AppName.content)

    def _section_update(self, k: int) -> None:
        super()._section_update(k)
        self.__dic[AppName.description] = self.get_command(AppName.description)
        self.__dic[AppName.content] = self.get_command(AppName.content)

    def _send_command(self, note: int, velo: int) -> None:
        if note not in NOTE_LETTER:
            MY_LOG.error(f"MIDI note: {note} is not expected. Check main.ini file")
        menu_key: str = f"{NOTE_LETTER[note]}-{velo}"
        command: str = self.get_command(menu_key)
        if not command:
            return
        for cmd in [x.strip() for x in command.split(":") if x.strip()]:  # commands separated by ":"
            msg = [convert_param(x) for x in cmd.split()]  # method name and arguments if any
            self._send_msg(msg)

        # after all commands send _redraw
        self._send_msg([AppName.client_redraw, self.__dic])


if __name__ == "__main__":
    pass
