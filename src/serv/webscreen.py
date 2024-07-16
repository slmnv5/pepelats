from multiprocessing import Queue, Event
from threading import Thread

from mvc.drawinfo import DrawInfo
from mvc.menuclient import MenuClient
from serv.webserver import MyServer, MyHandler


class WebScreen(MenuClient, MyServer):
    def __init__(self, q: Queue):
        MenuClient.__init__(self, q)
        MyServer.__init__(self)
        MyHandler.get_updates = self.get_updates
        self._has_update: Event = Event()
        Thread(target=self.serve_forever(), name="updater", daemon=True).start()

    def get_updates(self) -> DrawInfo:
        self._has_update.wait()
        self._has_update.clear()
        return self._di

    def _client_stop(self) -> None:
        super()._client_stop()
        self.shutdown()

    def _client_redraw(self, di: DrawInfo) -> None:
        super()._client_redraw(di)
        self._has_update.set()


if __name__ == "__main__":
    WebScreen(Queue())
