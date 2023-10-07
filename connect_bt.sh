#!/bin/bash

result=$(aconnect -l | grep "^client " | grep -i ssh)
if [ -n "$result" ]; then echo "Connected to client $result"; exit 0; fi


sudo bluetoothctl connect DC:86:D8:AF:D5:C5
if [ $? -eq 0 ]; then exit 0; fi

sudo bluetoothctl connect 9C:F4:8E:16:66:19 
if [ $? -eq 0 ]; then exit 0; fi

sudo bluetoothctl connect 58:E6:BA:67:24:64 
if [ $? -eq 0 ]; then exit 0; fi



exit 1


