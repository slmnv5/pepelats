from multiprocessing import Queue
from threading import Thread

from mvc.menuclient import MenuClient
from serv.webserver import MyServer
from utils.utilother import DrawInfo


class WebScreen(MenuClient, MyServer):
    def __init__(self, q: Queue):
        MenuClient.__init__(self, q)
        MyServer.__init__(self)
        Thread(target=self.serve_forever(), name="updater", daemon=True).start()

    def _client_stop(self) -> None:
        super()._client_stop()
        self.shutdown()

    def _client_redraw(self, di: DrawInfo) -> None:
        super()._client_redraw(di)


if __name__ == "__main__":
    WebScreen(Queue())
