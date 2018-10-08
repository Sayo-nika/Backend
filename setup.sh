#!/bin/sh

echo "-------- TODOs: --------"
grep -i "TODO" $(find . | grep .py$)
echo "------------------------"
