## Installation

*1) Install latest Raspberry Pi OS Lite (bookworm as of today).

*2) Install dependencies and LCD screen with driver running
script [install_dependencies.sh](./../config/etc/scripts/install_dependencies.sh)

*3) Clone this repository:

```
cd ~/; git clone https://github.com/slmnv5/pepelats
```

*4) To enable auto start edit ~/.bashrc file, append this line:

```
$HOME/pepelats/looper.sh
```

*5) Connect MIDI input controller and make sure it's name (or part of name) is listed in **main.ini** [MIDI] section
Alternatively you may plug USB keyboard and use keys listed in **main.ini**

### Command line parameters

Below parameters are used for troubleshooting

- --info -- verbose logging
- --debug -- more verbose logging
- --keep_screen -- keep logging output on screen to see errors

### Running on Windows:

When running on windows computer keyboard is used as MIDI controller. Keys to notes mapping is in **main.ini**:
