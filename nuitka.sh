#!/bin/bash

if pidof -o %PPID -x "nuitka.sh">/dev/null; then
    echo "Process already running"
    exit 1
fi

date > ./nohup.out

killall -9 python
pkill -9 looper.sh

D1="$HOME/musiloop"
D2="$HOME/pepelats"
EXE="$D2/main.dist/main.bin"

cd "$D1" || exit 1
python -m nuitka --standalone --output-dir="$D2/" --python-flag=-OO ./src/main.py

if [ "$?" -ne "0" ]; then exit 1; fi
if [ ! -f "$EXE" ]; then exit 1; fi

rsync  -avh --delete ./doc/ "$D2/doc/"
rsync  -avh --delete ./config/ "$D2/config/"
rsync  -avh --delete ./html/ "$D2/html/"
rsync  -avh --delete ./lib/ "$D2/lib/"
cp  -pv ./*.ini "$D2/"


cd "$D2" || exit 1
git add --all
git commit -m"auto commit new build"
git push

