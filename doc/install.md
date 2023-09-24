## Installation

* Install Raspberry Pi OS Lite, LCD screen with driver. To make text readable on 3.5 inch LCD select font Terminus 16x32
  using command below. The terminal will have 10 rows and 30 columns - good enough to see from 2-meter distance.

sudo dpkg-reconfigure console-setup

* Install dependencies running script [install_dependencies.sh](./../config/etc/scripts/install_dependencies.sh)

* Clone this repository:

```
cd ~/; git clone https://github.com/slmnv5/pepelats
```

* To enable auto start edit ~/.bashrc file, append this line:

```
$HOME/pepelats/looper.sh --count
```

### Command line parameters

- --count - [count notes](./input_controller.md) to increase number of available MIDI messages

Below parameters are used mostly for troubleshooting

- --kbd -- use computer keyboard to control looper. Main configuration file has mapping of keys to MIDI notes
- --info -- verbose logging
- --debug -- more verbose logging

### Running on Windows:

Looper is not designed for this, however it is possible to run on windows using this command:

```
python ./start_looper.py --info --kbd --count
```

Computer keyboard will send MIDI messages to control looper.


