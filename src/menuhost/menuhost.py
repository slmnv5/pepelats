from abc import ABC, abstractmethod
from multiprocessing import Queue
from time import sleep

# noinspection PyUnresolvedReferences
from menuhost.menuloader import MenuLoader
from utils.util_config import convert_param
from utils.util_log import MY_LOG
from utils.util_menu import NOTE_LETTER
from utils.util_name import AppName


class MenuHost(MenuLoader, ABC):
    """Translate notes to menu command and put into queue """

    def __init__(self, queue: Queue):
        MenuLoader.__init__(self)
        self.__dic: dict = dict()
        self.__queue: Queue = queue
        self._menu_update(AppName.play_section)
        self.__queue.put([AppName.client_redraw, self.__dic])
        self._alive: bool = True

    @abstractmethod
    def is_broken(self) -> bool:
        raise RuntimeError("This method should NOT be called()")

    def host_start(self) -> None:
        MY_LOG.info(f"MenuHost start working")
        while self._alive and not self.is_broken():
            sleep(5)
        self.__queue.put([AppName.client_stop])
        MY_LOG.info(f"MenuHost stop working")

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
        menu_command: str = self.get_command(menu_key)
        if not menu_command:
            return
        for cmd in [x for x in menu_command.split(":") if x.strip()]:  # commands separated by ":"
            lst = cmd.split()  # method name and arguments if any
            MY_LOG.debug(f"{self.__class__.__name__} sent command: {lst}")
            self.__process_list(lst)

        # after all commands send _redraw
        self.__queue.put([AppName.client_redraw, self.__dic])

    def __process_list(self, cmd: list) -> None:
        cmd = [cmd[0], *[convert_param(x) for x in cmd[1:]]]
        if cmd[0] == AppName.menu_update:
            self._menu_update(cmd[1])
        elif cmd[0] == AppName.section_update:
            self._section_update(cmd[1])
        elif cmd[0] == AppName.client_stop:
            self._alive = False
        else:
            self.__queue.put(cmd)


if __name__ == "__main__":
    pass
