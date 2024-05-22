## Installation

* Install latest Raspberry Pi OS Lite (bookworm as of today).

* Install dependencies and LCD screen with driver running
  script [install_dependencies.sh](./../config/etc/scripts/install_dependencies.sh)

* Clone this repository:

```
cd ~/; git clone https://github.com/slmnv5/pepelats
```

* To enable auto start edit ~/.bashrc file, append this line:

```
$HOME/pepelats/looper.sh
```

### Command line parameters

Below parameters are used for troubleshooting

- --info -- verbose logging
- --debug -- more verbose logging
- --keep_screen -- keep logging output on screen to see errors

### Running on Windows:

When running on windows computer keyboard is used as MIDI controller. Keys to notes mapping is in **main.ini**:
