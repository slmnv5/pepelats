## MIDI foot controller

Lopper accepts MIDI messages and using menu configuration files convert them into to looper's commands.
Buttons are few on most foot controllers, and looper has many more commands than available buttons. To deal with it
**multi tap mode** is used. If delay between taps is less than 0.6 seconds they belong to a series and produce a
different MIDI command.

As an example button A sends note 60, velocity = 100. Multiple tapping will send additional note 60 with changed
velocity. Changed velocity = number of taps + 5 if the last tap was a long hold. For this example:

- one tap sends note 60 with original velocity = 100 and note 60 with velocity = 1
- double tap sends note 60 with original velocity = 100 and note 60 with velocity = 2
- triple tap sends ..... velocity = 3
- one tap and hold sends ..... velocity = 1 + 5 = 6
- double tap and hold sends ..... velocity = 2 + 5 = 7

Using **multi tap mode** each button may send 6-7 times more of MIDI messages.

Multi tap uses 0.6 seconds delay to decide if there will be next tap. Because of this it should not be used for
time critical commands e.g. start playing or recording. But for other commands like changing volume it is
indispensable.

## MIDI input controller configurations

Foot controller is coupled with **menu configuration files** e.g. [play.ini](./../config/menu/6x4xN/play.ini) which
translate notes to looper commands.
There are few views each with its own menu: [menu_config.md](menu_config.md)

There are few configurations some using 4 buttons and some 6 buttons. Two rightmost buttons are
made by plugging in two ON/OFF momentarily switches into expression pedal input of **iRig BlueBoard MIDI foot controller
**. The looper converts control changes to note ON/OFF message



