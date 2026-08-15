#!/bin/bash

git switch main || exit 1
git branch -D temp
git checkout --orphan temp || exit 1
git add -A || exit 1
git commit -m "Initial commit" || exit 1
git branch -D main || exit 1
git branch -m main || exit 1
git push -f origin main || exit 1

echo "!!!!!!!! DONE PUSH !!!!!!!"
