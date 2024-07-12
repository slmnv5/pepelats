import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

from utils.htmlutil import FILE_FORM_HTML, MAIN_PAGE, LOAD_PREFIX, RESET_PREFIX, RESTART_PREFIX
from utils.utilconfig import ConfigName


def _split_post_data(post_data: str, bound: str, marker1: str, marker2: str) -> dict[str, str]:
    result = dict()
    l1, l2 = len(marker1), len(marker2)
    split_data = [x for x in post_data.split(bound)]
    split_data = [x for x in split_data if marker1 in x and marker2 in x]
    for x in split_data:
        i1 = x.index(marker1)
        i2 = x.index(marker2)
        k = x[i1 + l1: i2].strip('\'\" \r\n\t')
        v = x[i2 + l2:].strip()
        result[k] = v
    return result


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

    def _send_file_form(self, fname: str) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        if os.path.islink(fname):
            self.wfile.write(f"File is link: {fname}".encode("utf-8"))
        elif not os.path.isfile(fname):
            self.wfile.write(f"File not found: {fname}".encode("utf-8"))
        elif self.path[-4:] not in ['.ini', '.txt']:
            self.wfile.write(f"File type is incorrect: {fname}".encode("utf-8"))
        else:
            with open(fname, 'r') as f:
                data = f.read()
            html = FILE_FORM_HTML.format(file_name=fname, file_data=data)
            self.wfile.write(html.encode('utf-8'))

    def _send_main_page(self) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(MAIN_PAGE.encode('utf-8'))

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path == "/":
            self._send_main_page()
        elif self.path == RESET_PREFIX:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            result = subprocess.run(['git', 'reset', '--hard'], stdout=subprocess.PIPE)
            self.wfile.write(result.stdout)
        elif self.path == RESTART_PREFIX:
            os.system(ConfigName.kill_command)
        elif self.path.startswith(LOAD_PREFIX):
            fname = self.path[len(LOAD_PREFIX):]
            self._send_file_form(fname)
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
                self.wfile.write("Successfully updated file".encode())

    def _write_to_file(self) -> bool:
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()  # <--- Gets the data
        type_data = self.headers['Content-Type']
        type_list = type_data.split("boundary=")

        if len(type_list) != 2:
            self.send_error(400, "Bad Request", "Parsing form data failed on step 1")
            return False

        bound = "--" + type_list[1]  # separates each data item in post_data: k=v
        marker1 = 'Content-Disposition: form-data; name='  # placed before k=
        marker2 = '\r\n\r\n'  # placed after k=

        data_dict = _split_post_data(post_data, bound, marker1, marker2)

        if "file_name" not in data_dict or "file_data" not in data_dict:
            self.send_error(400, "Bad Request", "Parsing form data failed on step 2")
            return False

        fname = data_dict["file_name"]
        if not os.path.isfile(fname) or os.path.islink(fname):
            self.send_error(400, "Bad Request", "Parsing form data failed on step 3")
            return False

        with open(fname, 'w') as f:
            f.write(data_dict["file_data"])

        return True


def server_start():
    # noinspection PyTypeChecker
    httpd = HTTPServer(('', 8000), MyHandler)
    os.system('clear; echo To control looper connect to web IP address:; hostname -I; echo port 8000')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == '__main__':
    server_start()
