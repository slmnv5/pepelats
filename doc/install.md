## Installation

*1) Install latest **Raspberry Pi OS Lite 64 bit** (e.g. bookworm). I recommend **Raspberry Pi Imager**, it
does SSH and Wi-Fi setup for you. For all further configurations I recommend using SSH as you will need to run few
commands from your Raspberry Pi.
Assign simple host name to Raspberry Pi -- **'loop'** for easy connection later.

Login to your Raspberry Pi and run these commands. Here **r1.1.1.zip** -- is the version we need to install. Find out latest
version name on the project website.

```

wget https://github.com/slmnv5/pepelats/archive/refs/tags/r1.1.1.zip
unzip r1.1.1.zip -d ~/pepelats
sudo hostnamectl set-hostname loop

```

Optional. Install 3.5-inch LCD screen driver running script in: [install_lcd.sh](../etc/script/install_lcd.sh). This is not needed if you will use web interface.


To enable auto start edit ~/.bashrc file, append this line at the end.

```
# if only using web interface
$HOME/pepelats/loop.sh --web

# if only using LCD screen
$HOME/pepelats/loop.sh --lcd

# application will check and select interface
$HOME/pepelats/loop.sh

```

If using web connect to: http://loop.local:8000

### Optional LCD screen


Connect MIDI controller and make sure it's name (or part of name) is listed in file **user.ini**
in [MIDI] section.

Also make sure that MIDI controller notes are listed in file **user.ini** in [MIDI] section.


## Using computer typing keyboard as MIDI controller

If MIDI controller is missing you may use "--kbd" parameter in looper start up command.

### loop.sh script parameters

Below parameters may be used:

- --lcd -- use screen for looper state
- --web -- use web page for looper state
- --kbd -- use computer keyboard as MIDI controller. Keys are configured in user.ini file. Default six keys are: '
  1,2,3,4,q,w'
- --info -- verbose logging
- --debug -- more verbose logging

## Important files and directories

- log.txt -- is the log file for the current session.
- old.txt -- keeps about 1000 lines from past sessions.
- license.ini -- user's email and license number
- user.ini -- user specific configuration [main_config](main_config.md)
- ~/save_song -- directory where song files are saved
- config -- directory where configurations for drums and menus are stored
