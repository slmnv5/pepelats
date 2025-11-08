## Installation

*1) Install latest **Raspberry Pi OS Lite 64 bit** (e.g. bookworm). I recommend **Raspberry Pi Imager**, it
does SSH and Wi-Fi setup. For all further configurations use SSH.
Assign simple host name to Raspberry Pi (ex. **'loop'**) for easy connection later.

Install git:

```
sudo hostnamectl set-hostname loop

```

*2) Optional. Install 3.5-inch LCD screen driver running script in: [install_lcd.sh](../etc/script/install_lcd.sh), not needed
if using web.

*3) Clone this repository:

```
cd ~/; git clone https://github.com/slmnv5/pepelats
```

*4) To enable auto start edit ~/.bashrc file, append this line at the end.

```
$HOME/pepelats/loop.sh
```

*5) If using web connect to: http://loop.local:8000.

### Optional LCD screen

- Optional LCD screen may be installed by script [install_lcd.sh](
  ./../etc/script/install_lcd.sh)

*6) Connect MIDI controller and make sure it's name (or part of name) is listed in file **user.ini**
in [MIDI] section.

Also make sure that MIDI controller notes are listed in file **user.ini** in [MIDI] section.

If MIDI controller is missing you may use "--kbd" parameter as explained in next section.

*7) If you have terminal (LCD screen) connected, you need to change ~/user.ini file to use it as described
in [screen.md](screen.md). By default, web page is used to show looper state.

### loop.sh script parameters

Below parameters may be used:

- --lcd -- use screen for looper state
- --web -- use web page for looper state
- --kbd -- use computer keyboard as MIDI controller. Keys are configured in user.ini file. Default six keys are: '1,2,3,4,q,w'
- --info -- verbose logging
- --debug -- more verbose logging

## Important files and directories

- log.txt -- is the log file for the current session.
- old.txt -- keeps about 1000 lines from past sessions.
- license.ini -- user's email and license number
- user.ini -- user specific configuration [main_config](main_config.md)
- ~/save_song -- directory where song files are saved
- config -- directory where configurations for drums and menus are stored
