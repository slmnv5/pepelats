import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

IP_ADDRESS = "192.168.1.1"  # subprocess.check_output("hostname -I", shell=True)
BASE_DIR = None
LOAD_PREFIX = "/load?file="
LOAD_PREFIX_LEN = len(LOAD_PREFIX)
FNAME_END = "1.txt"

MAIN_HTML = """
<html>
<style>
h1 {text-align:center;}
p {text-align:center;}
table, th, td {
border: 5px solid grey; padding: 15px; text-align: left;
}
</style>
<head>
</head>
<body>
<table style="width:100%%">
<tr><td><h1>Selected files</h1></td><td><h1>All files</h1></td></tr>
<tr><td>%s</td><td>%s</td></tr>
</table>
</body>
</html>
"""

REDIRECT_HTML = """
<html>
<head>
	<meta http-equiv="refresh" content="0; url=http://%s:%s/login" />
</head>
<body>
	<b>Redirecting to login page</b>
</body>
</html>
""" % (IP_ADDRESS, 8000)

FILE_HTML = """
<html>
<style>
iframe { 
   position: absolute; 
   top: 3%%; 
   left:3%%; 
   width: 95%%; 
   height: 95%%;
} 
</style>
<head>
</head>
<body>
<iframe id="myFrame" src="%s"></iframe>

<script>
var frame = document.getElementById('myFrame');
	frame.onload = function () {
		var body = frame.contentWindow.document.querySelector('body');
		body.style.color = 'black';
		body.style.fontSize = '2vw';
	 };
</script>

</body>
</html>
"""


def recursive_files(dname: str) -> dict:
    matches = dict()
    for root, _, filenames in os.walk(dname):
        for fn in filenames:
            if fn.endswith(FNAME_END):
                relDir = os.path.relpath(root, dname)
                relFile = os.path.join(relDir, fn)
                matches[relFile] = fn
    return matches


class FileSelector:

    def __init__(self, dname: str):
        self.all_files = recursive_files(dname)
        self.selected_files = {}
        self.selectedFileName = os.path.join(dname, 'data.json')
        if os.path.isfile(self.selectedFileName):
            with open(self.selectedFileName, 'r') as fp:
                self.selected_files = json.load(fp)

    @staticmethod
    def decorate(keyValPair, linkStart):
        strTag = "<a href=%s%s>%s</a><br>" % (linkStart, keyValPair[0], keyValPair[1])
        return strTag

    def getSelected(self, linkStart):
        strTag = ""
        for x in self.selected_files.items():
            strTag += self.decorate(x, linkStart)
        return strTag

    def getAll(self, linkStart):
        strTag = ""
        for x in self.all_files.items():
            strTag += self.decorate(x, linkStart)
        return strTag


class CaptiveHandler(BaseHTTPRequestHandler):

    def send_Load(self):
        self.send_Head()
        filename = self.path[LOAD_PREFIX_LEN:]
        str1 = "./" + filename
        str2 = FILE_HTML % (str1)
        self.wfile.write(str2)

    def change_Mark(self):
        filename = self.path[LOAD_PREFIX_LEN:]
        dic1 = self.file_selector.selected_files
        dic2 = self.file_selector.all_files

        if filename in dic1:
            del dic1[filename]
        elif filename in dic2:
            value = dic2[filename]
            dic1[filename] = value

        with open(self.file_selector.selectedFileName, 'w') as fp:
            json.dump(dic1, fp)

        self.send_Main()

    def send_Main(self):
        self.send_Head()
        str1 = MAIN_HTML % (self.file_selector.getSelected(LOAD_PREFIX), self.file_selector.getAll(LOAD_PREFIX))
        self.wfile.write(str1)

    def send_Binary(self, filename):
        f = open(filename, "rb")
        str1 = f.read()
        f.close()
        self.wfile.write(str1)

    def send_Redir(self):
        self.send_Head()
        self.wfile.write(REDIRECT_HTML)

    def send_Head(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith(LOAD_PREFIX):
            return self.send_Load()

        if self.path.startswith("/login"):
            return self.send_Main()

        isLocal = self.path.startswith("/")
        fileExists = os.path.isfile("." + self.path)
        if isLocal and fileExists:
            return self.send_Binary("." + self.path)

        return self.send_Redir()


if __name__ == '__main__':

    IP_TABLES_COMMANDS = []
    BASE_DIR = os.path.expanduser("~/Dropbox/mypi/music")
    if not os.path.isdir(BASE_DIR):
        BASE_DIR = os.path.expanduser("~/mypi/music")
        if not os.path.isdir(BASE_DIR):
            sys.exit("Root directory not found: " + BASE_DIR)

    SAVEPATH = os.getcwd()
    os.chdir(BASE_DIR)
    print(11111111111111)
    os.getcwd(), SAVEPATH

    my_serv1 = HTTPServer(('', 8000), CaptiveHandler)
    my_serv1.file_selector = FileSelector(BASE_DIR)

    try:
        my_serv1.serve_forever()
    except KeyboardInterrupt:
        print("closed")

    my_serv1.server_close()

    os.chdir(SAVEPATH)
