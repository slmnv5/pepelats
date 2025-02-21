#!/bin/bash

D1="$HOME/musiloop"
D2="$HOME/pepelats"

cd "$D1" || exit 1
git reset --hard
git pull

cd "$D2" || exit 1
git reset --hard
git pull

cd "$D1"

