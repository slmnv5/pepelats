## Installation

- Install latest **Raspberry Pi OS Lite 64 bit** (e.g. bookworm). I recommend **rpi imager** that allows to configure
  Wi-Fi (network ID and password) and SSH (enable ssh and set username/password). Also assign host name **'loop'**.

- Connect via ssh to rpi box and run commands shown below.
  Here **r1.1.5.zip** -- is the version to install. Find out the latest version name on the project website.

```
ssh pi@loop.local
sudo apt install libportaudio2
wget https://github.com/slmnv5/pepelats/archive/refs/tags/r1.1.5.zip
unzip r1.1.5.zip -d ~/pepelats
```

- To enable auto start edit ~/.bashrc file, append this line at the end.

```
$HOME/pepelats/loop.sh
```

- The looper shows status on the web page: http://loop.local:8000
  This page allows you to edit configuration files of the looper and see messages in log files.
  Sample configuration is accessible in starting page, use it as example to modify your personal configuration.

- Connect MIDI controller and make sure it's name (or part of name) is listed in file user configuration.
  Check log file for any errors related to MIDI connection or audio device connection.

Also make sure that MIDI controller notes are listed in file **user.ini** in [LOOPER] section.

## Important files and directories

- log.txt -- is the log file for the current session.
- old.txt -- keeps about 1000 lines from past sessions.
- license.ini -- user's email and license number
- user.ini -- user specific configuration [main_config](main_config.md)
- main.ini -- sample configuration, not editable
- ~/save_song -- directory where song files are saved
- config -- directory where configurations for drums and menus are stored
