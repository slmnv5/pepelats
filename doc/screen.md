## Screen

Looper outputs its state on text terminal or on a web page.
This depends on option **screen_type** in **[LOOPER]** section of [**main.ini**](./../main.ini)

In case of screen_type = 0 the output goes to stdout stream. In case of screen_type = 1 the output goes to web page, e.g. http://192.168.1.3:8000

Actual IP address depends on LAN configuration.
HTTP port used is always 8000.
