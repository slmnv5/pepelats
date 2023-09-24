#!/bin/bash

# commands to pair and connect a bluetooth device
#sudo service bluetooth restart
#sudo service bluetooth status
#sleep 2
#sudo hciconfig hci0 sspmode 0
sudo bluetoothctl << EOF1
power on
pairable on
discoverable on
default-agent
trust 58:E6:BA:67:24:64
disconnect 58:E6:BA:67:24:64
connect 58:E6:BA:67:24:64
paired-devices
quit

EOF1

#58:E6:BA:67:24:64