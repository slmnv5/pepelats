import os

LOAD_PREFIX = "/load?file="
RESET_PREFIX = "/reset"
RESTART_PREFIX = "/restart"


def _one_link(fname: str) -> str:
    return f"<a href = {LOAD_PREFIX}{fname}>{fname}</a><br/>"


def _all_links(dname: str, end_with: str) -> str:
    file_lst = list()

    for root, _, files in os.walk(dname):
        for fname in [os.path.join(root, x) for x in files if x.endswith(end_with)]:
            file_lst.append(fname)
    link_lst = list()
    for fname in file_lst:
        link_lst.append(_one_link(fname))
    return "\n".join(link_lst)


_MAIN_PAGE_HTML = """
<html><head></head><body>
<h1>Actions</h1>
<a href={}>Restart looper</a><br/>
<a href={}>Reset all config to factory</a><br/>
<h1>Check log file for errors</h1> {}
<h1>Edit main config files</h1> {}
<h1>Edit drum config files</h1> {}
<h1>Edit menu config files</h1> {}
</body></html>
"""

# noinspection SpellCheckingInspection
FILE_FORM_HTML = """
<html><head></head><body>
<form action="save_file" method="post" enctype='multipart/form-data'>
    <p>
        <b>File name:</b>
        <input type="text" name="file_name" value="{file_name}" readonly/>
        <input type="submit" value="Save file"/>
    </p>
    <textarea autocapitalize="off" cols="150" name="file_data" rows="30" spellcheck="false">
    {file_data}
    </textarea>
</form>
</body></html>
"""

MAIN_PAGE = _MAIN_PAGE_HTML.format(RESTART_PREFIX, RESET_PREFIX, _one_link("./log.txt"),
                                   _one_link("./main.ini") + _one_link("./local.ini"),
                                   _all_links("./config/drum", ".ini"),
                                   _all_links("./config/menu", ".ini"))
