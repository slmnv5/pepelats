#!/bin/bash

git branch -D temp
git checkout --orphan temp
git add .
git commit -m "Initial commit"
git branch -D main
git branch -m main

git push -f --set-upstream origin main
