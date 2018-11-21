#!/bin/sh

echo "-------- TODOs: --------"
grep -i "TODO" $(find -wholename "./*/*.py"  | grep .py$)
grep -i "TODO" $(find -wholename "./services/*.js" | grep .js)
echo "------------------------"

