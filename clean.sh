#!/bin/bash

cd "$(dirname "$0")" || exit 1

git checkout --orphan temp
git add -A
git commit -m "Initial commit"
git branch -D main
git branch -m main
git push -f --set-upstream origin main
