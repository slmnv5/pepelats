# Pepelats – audio looper with drums


## Installation

- Install latest Raspberry Pi OS Lite 64 bit. I recommend rpi imager that allows to configure Wi-Fi (network ID and password). Assign host name (example: loop). 

- Connect keyboard and HDMI display or, better, connect via SSH from another computer and run this command to install looper.

- To download and run the installer script automatically, copy and paste one of the following commands into your terminal.
This script will download `pepelats.zip`, install to `~/pepe/` directory, append startup command to `~/.profile`

```bash
wget -qO- https://github.com/slmnv5/pepelats/releases/latest/download/install.sh | bash
```

- Connect MIDI controller and make sure it's name (or part of name) is listed in user.ini file.
- Also check that MIDI controller notes for your specific controller are listed in user.ini
- If your MIDI controller uses Bluetooth you need to run few commands on Raspberry Pi to pair and connect it.
- You may use computer keyboard instead of MIDI controller as described below. Do this for quick start and leave MIDI configuration for later especially if your controller uses Bluetooth.
- Finally, you need to check log file for any errors related to MIDI connection or audio device connection.
- You may do most of the above via the application [main page](../index.html) that has links to configurations and logs.

### Important files you may view / edit from main page

- log.txt – log file for current session
- old.txt – log that keeps about 1000 lines from past sessions
- main.ini – default configuration, serves as an example
- user.ini – user specific configuration, overrides defaults
- license.ini – user's email and license number

### Important directories

- ~/save_song – directory where song files are saved
- ./config – directory where configurations for drums and menus are stored

## Configuration details

All configurations are in two files: 

- [main.ini](../main.ini) - contains all default configurations and comments explaining each option
- user.ini - user configuration, initially empty, edit this file to override defaults. You may edit file user.ini on the [main page](../index.html).

### Configurations for Audio and MIDI

- audio_names – list of names (or part of names) of audio devices, case-sensitive. First found device in the list will be used. If nothing is found looper will start anyway, and you may check the log for details and errors.
- midi_in_names – list of names (or part of names) for MIDI input controls, case-sensitive. First found device in the list will be used. If nothing is found looper will try to use computer keyboard. If later is not found looper will start anyway, and you may check the log to see details and errors.
- midi_values – MIDI notes (or CC) numbers that MIDI device sends. This is list of integer values from 0 to 127.
- keyboard_keys – computer keyboard keys to use for MIDI messages. Defaults are: 1, 2, 3, 4, q, w 

### Checking errors and correcting configurations

If MIDI input and / or audio device not found the looper starts anyway and saves errors in the log. There are 3 ways to run it and fix any issues

- No screen, no SSH connection, there is Wi-Fi connection – status on [main page](../index.html), you can check log for errors, edit configurations and restart looper.
- Screen connected to Raspberry Pi – status on screen. You need computer keyboard to run commands, check logs, edit configurations and restart looper.
- Looper started via SSH connection – status on SSH terminal, similar to the previous case, but you work from another computer.

## MIDI controller and multi-tapping

There are only few buttons on foot controllers and number of looper commands is much bigger. To deal with it multi-tapping is used. If delay between taps is less than 0.5 seconds they belong to one series and produce MIDI note as explained below. 

Assume button A sends note ON for note 60 with velocity 100. Multiple tapping will send one additional note ON for note 60 with changed velocity.   
This additional note ON message will have velocity equal to number of taps + 5 if there is a hold in the end. For this example: 

- one tap: note 60 velocity = 100 + note 60 velocity = 1
- double tap: note 60 velocity = 100 + note 60 velocity = 2
- triple tap: note 60 velocity = 100 + note 60 velocity = 3
- one tap + hold: note 60 velocity = 100 + note 60 velocity = 1 + 5 = 6
- double tap + hold: note 60 velocity = 100 + note 60 velocity = 2 + 5 = 7

Using multi-taps one button sends different MIDI messages with velocities 1,2,3... Multiple taps use 0.5 seconds delay to see if there is a next tap. Because of this it should not be used for time critical commands – like play start or stop. Use it for other commands like changing volume, scrolling song list, etc. 

### Menu files – link buttons, MIDI messages and actions

In menu files we use button label A and number of taps to assign actions: 

- A: play 0
- A1: add_loop: record 
- A2: stop_play: stop_drum

Here A – is original note sent instantly without any delay (note 60 with original velocity). A1, A2 – are counted notes delayed by 0.5 seconds + time it takes to tap 1 or 2 or times (note 60, velocity 1 and 2 respectively). 
Note that actions may have parameters (ex: 'play 0') and may be chained one after another separated by colon.

### Control change MIDI messages

If foot controller sends control change (CC) messages (e.g.from expression pedal) the looper can convert them into notes. As example CC 12 will be converted to note 12 ON/OFF. 

If a MIDI controller has expression pedal input we may plug ON/OFF button and use it with the looper. This is how 2 more buttons were added to iRig BlueBoard MIDI controller.

## Menu

Menu configurations are INI files that link together button labels, MIDI messages and looper commands.  Additionally, menu files have two options:

- description – text appearing on top of screen when menu is loaded, just below the loop progress bar.
- show – a command to display looper information on screen

There are only three menu configurations files.

- [play.ini](../config/menu/play.ini) - play / record / clear song parts and switching between them. Show loops for song part. Silence, delete, re-arrange loops.
- [song.ini](../config/menu/song.ini) - delete, save, load, initialize song. Select drum configuration.
- [serv.ini](../config/menu/serv.ini) - restart looper, show hardware ID and license. Select drum type, adjust drum volume, parameter.

Each menu file has two sections with different but related commands. As an example play menu has section to work with song parts and section to work with loops inside one part.

When switching menu file or menu section the look of the screen changes. However, there is common information shown for each menu. Namely, the top row always shows progress bar. It includes position of the loop, current song name, drum configuration and beats per minute.

## Song

Song is collection of recorded song parts along with specific drum type and drum configuration. Songs are saved in user's home directory ~/save_song. 

Song names are 'random words' and include Drum style name (ex: Disco, Blues,...) and sampling frequency (ex: k48, k44,). The latter prevents loading song recorded on a devices with different sampling frequency. 

## Screen

Looper outputs its state on: 

- text screen – attached screen via SPI or HDMI connection
- web page – http://loop.local:8000 Here 'loop' is host name of raspberry pi and HTTP port is always 8000 

If screen is attached – it is used, otherwise web page is used to output looper state.

- Web page pros: It allows you to see log files, edit configuration files, restart looper.
- Web page cons: You need to carry a device with web browser (phone, tablet) that is connected to the same Wi-Fi as the looper.
- LCD screen pros: If we use special 3.5 inch LCD for Raspberry Pi it will make a simple compact looper that does not need Wi-Fi connection.
- LCD screen cons: Hard to change configuration or check logs for errors. Best way is to connect Raspberry Pi to Wi-Fi and use another computer over SSH connection.

## Drums in general

Looper has embedded drum machine that may use different drums: 

- Style drum – using text patterns – with drum names, steps and accents
- MIDI drum – using text file configurations to send MID commands (stop, set BPM, start of loop, etc.)
- Loop drum – the first recorded song part becomes a drum track.

### Drum breaks

There are two modes for drums – normal beat and break. Different types of drums implement breaks as described here. 

- Style drum patterns are split into 2 groups based on the name – if pattern name contains "break" it is used for breaks otherwise it is used for beats. If drums are not found for breaks or for beats, this feature does not work.
- Loop drum mutes some loops to play variations and breaks. If song part does not have enough loops for breaks this feature does not work.
- MIDI drum break may be configured in INI file by sending specific MIDI command. This command may be program change or other command specific for connected drum machine. Again, if program change command is not set correctly, this feature does not work.

### Drum random variations

Every drum has randomness parameter that can be adjusted and saved with the song. If this parameter = 0.5 then there is 50% chance that drum pattern will be randomized at start of bar. For new song this parameter = 0.1 

If there is only one pattern for Style drum, random variations do not work.  Similarly, if there are not enough loops for Loop drum this feature does not work.

## Style drum

Style drum is using text patterns specific for musical style and sample WAV files to produce drum accompaniment. Each style pattern sits inside one section of INI file. Number of steps is equal to the longest drum length. Two examples of styles are below.

- [Metronome](../config/drum/style/Metronome.ini) – patterns for metronome
- [Blues](../config/drum/style/Blues.ini) – patterns for blues
- [Twist](../config/drum/style/Twist.ini) – patterns for twist

Drum sample names used in pattern and WAV file names are the same (ex. sd.wav, bd.wav).

## Loop drum

Loop drum is just a recorded song part that plays along with other parts. As any song part it may have many parallel loops, and it is randomized by muting some of them. It has INI configuration that defines how beats and breaks are played and randomized. Four small numbers (1-9) are used, two numbers for beats and two for breaks. For convenience these numbers are included in configuration file name and inside the file there is description of the logic.

- [lp-12-12.ini](../config/drum/loop/lp-12-12.ini)
- [lp-23-11.ini](../config/drum/loop/lp-23-11.ini)

To fully utilize breaks and random variations features the song part needs to record sufficiently many loops. Thus, for example, if song part has only one loop the drum will work but drum breaks and random variations will not work.

## MIDI drum

MIDI drum sends MIDI messages to external drum machine to synchronize it with the looper, change drum volume, program number, etc.

Set of MIDI messages along with the MIDI OUT port name are saved in configuration INI file. There are three ready-made configurations that may serve as examples.

- [ValGP-100.ini](../config/drum/midi/ValGP100.ini) - Valeton GP100 guitar pedal with drums.
- [MidiFire.ini](../config/drum/midi/MidiFire.ini) – MidiFire IOS application that sets dynamic MIDI clock and can control other IOS drum applications.
- [FunkBox.ini](../config/drum/midi/FunkBox.ini) – Funk Box IOS drum application. 

### MIDI messages and variables used in configuration

There are six messages to control MIDI device, each may contain variables:

- **stop_msg** sent when drum stops, usually no variables used
- **tap_msg** set BPM by tap tempo, usually no variables used
- **bar_msg** sent at start of each bar, likely to use COUNT variable
- **prog_msg** sent when prog changes, likely to use PROG variable
- **volume_msg** sent when volume changes, use VOLUME variable
- **bpm_msg** set BPM, use BPM or BPM_LIST variables


There are five message variables with value examples:

- **BPM** (= 123.89) - beats per minute
- **BPM_LIST** (= \[0,1,2,3,8,9\]) - BPM as list of bytes for SysEx message
- **COUNT** (= 12) - count of bars since start from 0
- **PROG** (= 125) - MIDI prog. value from 0 to 127
- **VOLUME** (= 0.85) - drum volume form 0.0 to 1.0

### MIDI out port for MIDI drum

Each drum configuration INI file has option "midi_out_name". This is MIDI port name (or part of the name) used to send MIDI drum messages. If port is not available (device is not connected) the drum still be loaded but messages not sent. Drum configuration view will show port drum name as "None". After MIDI drum is connected you need to re-load song or set drum configuration file so that looper will connect to the port. 

## Troubleshooting errors

Sometimes your audio device may have issues with audio capture or playback volume. 
To fix you need install a text user interface (TUI) command so that you can see and change playback and recording volumes.

```bash
sudo apt install alsa-utils
alsamixer
```
I recommend setting levels for playback and recording around 80-90%. 
If your recording after capture sounds louder you need to decrease capture level. 

Advanced audio devices as a rule have all these levels regulated in hardware. Only basic USB devices that do not have any knobs need adjusting levels by software settings.

To save the setting that you made run this:
```bash
sudo alsactl store
```
Setting are saved for each device separately and restored after device is connected.

### Changing log settings

If you have errors you need to connect to Raspberry pi box using SSH and run this commands:
```bash
cd ~/pepe;

./loop.sh --debug;

cat log.txt
```
The logging levels: --warn, --info and especially –-debug will provide more details in the log file.

Finally, if you connect via SSH and want to run looper and work with logs and configuration using web browser run this:
```bash
cd ~/pepe

./loop.sh --debug –web
```