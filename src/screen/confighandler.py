import os
import subprocess
from configparser import ConfigParser, ParsingError
from http.server import BaseHTTPRequestHandler, HTTPServer

from utils.util_config import CONFIG_PORT, LOCAL_IP
from utils.util_log import MY_LOG
from utils.util_other import split_to_dict
from utils.util_web import CONFIG_PAGE_B, RESET_PATH, EXIT_PATH, EDIT_PATH, SHOW_PATH, \
    FAVICON_B, load_file


def web_config():
    # noinspection PyTypeChecker
    server = HTTPServer(("", CONFIG_PORT), ConfigHandler)
    MY_LOG.warning(f"HTTP server starting at: {LOCAL_IP}:")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


class ConfigHandler(BaseHTTPRequestHandler):

    def send_hdr(self, status: int = 200, arg_dic=None) -> None:
        d: dict[str, str] = {'Content-type': 'text/html'}
        if arg_dic is not None:
            d.update(arg_dic)
        self.send_response(status)
        for k, v in d.items():
            assert isinstance(k, str) and isinstance(v, str), f"must be strings: k={k}, v={v}"
            self.send_header(k, v)
        self.end_headers()

    def _write_to_file(self) -> bool:
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()  # <--- Gets the data
        type_list = self.headers.get('Content-Type', "").split("boundary=")

        if len(type_list) != 2:
            return False

        bound = "--" + type_list[1]  # separates each data item in post_data: k=v
        mark1 = 'Content-Disposition: form-data; name='  # placed before k=
        mark2 = '\r\n\r\n'  # placed after k=
        data_dict = split_to_dict(post_data, bound, mark1, mark2, '\'\" \r\n\t', ' \r\n\t')

        if "file_name" not in data_dict or "file_data" not in data_dict:
            return False

        fname = data_dict["file_name"]
        if not os.path.isfile(fname) or os.path.islink(fname):
            return False

        if fname[-4:].lower() == ".ini":
            cfg = ConfigParser()
            try:
                cfg.read_string(data_dict["file_data"])
            except ParsingError as ex:
                self.wfile.write(f"Parsing form data failed: {ex}".encode())
                return False

        with open(fname, 'w') as f:
            f.write(data_dict["file_data"])
        return True

    def _send_file(self, fname: str, read_only: bool) -> None:
        self.send_hdr()
        if os.path.islink(fname):
            self.wfile.write(f"File is link: {fname}".encode())
        elif not os.path.isfile(fname):
            self.wfile.write(f"File not found: {fname}".encode())
        else:
            data = load_file(fname)
            disabled = "disabled" if read_only else ""
            html = load_file("html/file_form.html")
            html = html.format(disabled=disabled, file_name=fname, file_data=data)
            self.wfile.write(html.encode())

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path == "/":
            self.send_hdr()
            self.wfile.write(CONFIG_PAGE_B)
        elif self.path == RESET_PATH:
            self.send_hdr()
            result = subprocess.run(['git', 'reset', '--hard'], stdout=subprocess.PIPE)
            self.wfile.write(result.stdout)
        elif self.path == EXIT_PATH:
            raise KeyboardInterrupt()
        elif self.path.startswith(EDIT_PATH):
            fname = self.path[len(EDIT_PATH):]
            self._send_file(fname, False)
        elif self.path.startswith(SHOW_PATH):
            fname = self.path[len(SHOW_PATH):]
            self._send_file(fname, True)
        elif self.path == "/favicon.ico":
            self.send_hdr(arg_dic={'Content-type': 'application/octet-stream'})
            self.wfile.write(FAVICON_B)
        else:
            self.send_hdr(303, arg_dic={'Location': '/'})

    # noinspection PyPep8Naming
    def do_POST(self):
        if self.path != "/save_file":
            self.send_hdr(303, arg_dic={'Location': '/'})
        else:
            if self._write_to_file():
                self.send_hdr(303, arg_dic={'Location': '/'})
            else:
                self.send_error(400, "Bad Request", "Could not save file")

    def log_message(self, format1, *args):
        pass


if __name__ == "__main__":
    web_config()
