#!/bin/sh

echo "-------- TODOs: --------"
grep -i "TODO" $(find . -type d \( -path mods -o -path routes \) -prune -o -print | grep .py$)
grep -i "TODO" $(find ./services/| grep .js$)
echo "------------------------"

