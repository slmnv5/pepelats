## Installation

*1) Install latest **Raspberry Pi OS Lite 64 bit** (e.g. bookworm). I recommend **rpi imager**, it
does SSH and Wi-Fi setup for you. Use SSH to run commands shown below.
Assign simple host name to Raspberry Pi e.g. **'loop'** for easy connection later.

Login to your Raspberry Pi and run these commands. Here **r1.1.5.zip** -- is the version to install. Find out
latest version name on the project website.

```
sudo apt install libportaudio2
wget https://github.com/slmnv5/pepelats/archive/refs/tags/r1.1.5.zip
unzip r1.1.5.zip -d ~/pepelats
sudo hostnamectl set-hostname loop

```
To enable auto start edit ~/.bashrc file, append this line at the end.

```
$HOME/pepelats/loop.sh
```

If using web connect to: http://loop.local:8000

Connect MIDI controller and make sure it's name (or part of name) is listed in file **user.ini**
in [LOOPER] section.

Also make sure that MIDI controller notes are listed in file **user.ini** in [LOOPER] section.

## Important files and directories

- log.txt -- is the log file for the current session.
- old.txt -- keeps about 1000 lines from past sessions.
- license.ini -- user's email and license number
- user.ini -- user specific configuration [main_config](main_config.md)
- ~/save_song -- directory where song files are saved
- config -- directory where configurations for drums and menus are stored
