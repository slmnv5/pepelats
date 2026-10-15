#!/bin/bash

cd "$(dirname "$0")" || exit 1

git checkout --orphan temp || exit 1
git add -A || exit 1
git commit -m "Initial commit" || exit 1
git branch -M main || exit 1
git push -f --set-upstream origin main
