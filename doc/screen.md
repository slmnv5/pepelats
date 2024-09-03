## Screen

Looper outputs its state on text terminal or on web page.
This depends on option **screen_type** in **SCREEN** section of [**main.ini**](./../main.ini)

To override configuration in INI file use command line options "--text" or "--web"
In case of screen_type = 0 (--text) the output goes to stdout stream
In case of screen_type = 1 (--web) the output goes to web page, e.g. http://192.168.1.3:8000/
Actual IP address depends on LAN configuration.  
