#!/bin/bash

cd "$(dirname "$0")" || exit 1

rsync -avh pi@loop.local:~/pepelats/pepelats.zip  ./



