## Installation

*1) Install latest **_Raspberry Pi OS Lite_** (bookworm as of today).

*2) Optional. Install LCD screen driver running script in:  
[install_lcd.sh](../etc/scripts/install_lcd.sh)

*3) Clone this repository:

```
cd ~/; git clone https://github.com/slmnv5/pepelats
```

*4) To enable auto start edit ~/.bashrc file, append this line:

```
$HOME/pepelats/looper.sh
```

*5) Connect MIDI controller and make sure it's name (or part of name) is listed in [main.ini](./../main.ini) [MIDI] section and the
notes it sends are listed there as well.

If MIDI controller is not found and computer keyboard is connected it will be used for control.   
Keys are configured in main.ini file. Default keys are: '1,2,3,4,q,w'.

### Command line parameters

Below parameters are used for troubleshooting

- --info -- verbose logging
- --debug -- more verbose logging
- --kbd -- use keyboard instead of MIDI controller

## Important files
log.txt -- is the log file for the latest session.
log.bak -- keeps about 1000 lines from the past sessions.
main.ini -- default configuration of the looper
local.ini -- user's customized configuration of looper
config -- directory where configurations for drums, and menus are stored
~/save_song -- director where song files are saved
