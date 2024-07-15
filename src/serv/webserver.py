import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

from utils.utilconfig import ConfigName, IP_ADDR
from utils.utilother import split_to_dict

_EDIT_PATH = "/edit?file="
_SHOW_PATH = "/show?file="
_RESET_PATH = "/reset"
_EXIT_PATH = "/exit"


def _load_html_file(fname: str) -> str:
    assert os.path.isfile(fname)
    with open(fname, 'r') as f:
        return f.read()


def _one_link(fname: str) -> str:
    return f"\n<a href = {_EDIT_PATH}{fname}>{fname}</a>"


def _all_links(dname: str, end_with: str) -> str:
    file_lst = list()

    for root, _, files in os.walk(dname):
        for fname in [os.path.join(root, x) for x in files if x.endswith(end_with)]:
            file_lst.append(fname)
    link_lst = list()
    for fname in file_lst:
        link_lst.append(_one_link(fname) + "<br/>")
    return "".join(link_lst)


class MyHandler(BaseHTTPRequestHandler):

    def _send_binary(self, fname):
        self.send_response(200)
        self.send_header('Content-type', ' application/octet-stream')
        self.end_headers()
        with open(fname, "rb") as f:
            data = f.read()
        self.wfile.write(data)

    def _send_redirect(self) -> None:
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/')  # This will navigate to the original page
        self.end_headers()

    def _send_file(self, fname: str, send_form: bool) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        if os.path.islink(fname):
            self.wfile.write(f"File is link: {fname}".encode("utf-8"))
        elif not os.path.isfile(fname):
            self.wfile.write(f"File not found: {fname}".encode("utf-8"))
        elif self.path[-4:] not in ['.ini', '.txt'] or self.path[-3:] not in ['.md']:
            self.wfile.write(f"File type is incorrect: {fname}".encode("utf-8"))
        else:
            with open(fname, 'r') as f:
                data = f.read()
            html = data if not send_form else WebHelper.file_form.format(file_name=fname, file_data=data)
            self.wfile.write(html.encode('utf-8'))

    def _send_config_page(self) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(WebHelper.config_page)

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path == "/":
            self._send_config_page()
        elif self.path == _RESET_PATH:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            result = subprocess.run(['git', 'reset', '--hard'], stdout=subprocess.PIPE)
            self.wfile.write(result.stdout)
        elif self.path == _EXIT_PATH:
            raise KeyboardInterrupt()
        elif self.path.startswith(_EDIT_PATH):
            fname = self.path[len(_EDIT_PATH):]
            self._send_file(fname, True)
        elif self.path.startswith(_SHOW_PATH):
            fname = self.path[len(_SHOW_PATH):]
            self._send_file(fname, False)
        elif self.path == "/favicon.ico":
            self._send_binary("./favicon.ico")
        else:
            self._send_redirect()

    # noinspection PyPep8Naming
    def do_POST(self):
        if self.path != "/save_file":
            self._send_redirect()
        else:
            if self._write_to_file():
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write("Successfully updated file".encode("utf-8"))

    def _write_to_file(self) -> bool:
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")  # <--- Gets the data
        type_list = self.headers.get('Content-Type', '').split("boundary=")

        if len(type_list) != 2:
            self.send_error(401, "Bad Request", "Parsing form data failed")
            return False

        bound = "--" + type_list[1]  # separates each data item in post_data: k=v
        mark1 = 'Content-Disposition: form-data; name='  # placed before k=
        mark2 = '\r\n\r\n'  # placed after k=
        data_dict = split_to_dict(post_data, bound, mark1, mark2, '\'\" \r\n\t', ' \r\n\t')

        if "file_name" not in data_dict or "file_data" not in data_dict:
            self.send_error(402, "Bad Request", "Parsing form data failed")
            return False

        fname = data_dict["file_name"]
        if not os.path.isfile(fname) or os.path.islink(fname):
            self.send_error(403, "Bad Request", "Parsing form data failed")
            return False
        with open(fname, 'w') as f:
            f.write(data_dict["file_data"])

        return True


class WebHelper:
    file_form: str = _load_html_file("html/file_form.html")
    tmp: str = _load_html_file("html/config_page.html")

    format_lst: list[str] = list()
    format_lst.append(_EXIT_PATH)
    format_lst.append(_RESET_PATH)

    format_lst.append(_one_link("./main.ini"))
    format_lst.append(_one_link("./local.ini"))
    format_lst.append(_one_link("./log.txt"))

    format_lst.append(_all_links(f"{ConfigName.drum_config_dir}", ".ini"))
    format_lst.append(_all_links(f"./{ConfigName.menu_config_dir}", ".ini"))
    format_lst.append(_all_links(f"./{ConfigName.documents_dir}", ".md"))
    assert len(format_lst) == tmp.count('{}')
    config_page: bytes = tmp.format(*format_lst).encode('utf-8')


def webserver_start():
    print(f"To control looper connect to:\nhttp://{IP_ADDR}:8000")
    # noinspection PyTypeChecker
    server = HTTPServer(('', 8000), MyHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == "__main__":
    webserver_start()
