## Screen

Looper outputs its state on text terminal or on a web page.
This depends on option **use_web** in **[LOOPER]** section of [**main.ini**](./../main.ini)

If use_web = 0 the output goes to stdout stream.

If use_web = 1 the output goes to URL: http://loop.local:8000

Here 'loop' is host name set in [install.md](install.md) and HTTP port is always 8000.
