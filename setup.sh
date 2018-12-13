#!/bin/sh

echo "-------- TODOs: --------"
grep -i "TODO" $(find -wholename "./*/*.py"  | grep .py)
grep -i "TODO" $(find -wholename "./services/*.js" | grep .js)
echo "------------------------"

echo "-------- FIXMEs: --------"
grep -i "FIXME" $(find -wholename "./*/*.py"  | grep .py)
grep -i "FIXME" $(find -wholename "./services/*.js" | grep .js)
echo "------------------------"
