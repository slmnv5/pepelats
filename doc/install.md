## Installation

*1) Install latest **Raspberry Pi OS Lite 64 bit** (e.g. bookworm). I recommend **Raspberry Pi Imager** for that, it can
enable SSH connection and configure Wi-Fi password. For all configuration and management I recommend using SSH.
Also, I recommend to assign simple host name (ex. **'loop'**) for esy connection later.

Install git:

```
sudo apt install git

sudo hostnamectl set-hostname loop

```

*2) Optional. Install LCD screen driver running script in: [install_lcd.sh](../config/script/install_lcd.sh), not needed
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
  ./../config/script/install_lcd.sh)

*6) Connect MIDI controller and make sure it's name (or part of name) is listed in file **local.ini**
in [MIDI] section.

Also make sure that MIDI controller notes are listed in file **local.ini** in [MIDI] section.

If MIDI controller is missing you may use "--kbd" parameter as explained in next section.

*7) If you have terminal (LCD screen) connected, you need to change ~/local.ini file to use it as described
in [screen.md](screen.md). By default, web page is used to show looper state.

### Loop.sh script parameters

Below parameters may be used:

- --info -- verbose logging
- --debug -- more verbose logging
- --kbd -- use computer keyboard as MIDI controller. Keys are configured in local.ini file.
  Default six keys are: '1,2,3,4,q,w'.

## Important files and directories

- ~/log.log -- is the log file for the current session.
- ~/old.log -- keeps about 1000 lines from past sessions.
- ~/local.ini -- user's configuration [main_config](main_config.md)
- ~/save_song -- directory where song files are saved
- config -- directory where configurations for drums, and menus are stored
