#!/usr/bin/env bash
# This is to be used only if something is wrong with current gh-pages
# It first deletes current gh-pages branch and then pushing everything anew

# Ensure that the CWD is set to script's location
cd "${0%/*}"
CWD=$(pwd)
cd ..

#######

if [ $# -eq 1 ] && [ $1 = "-f" ]; then
	echo "Redeploying ..."
	git push origin --delete gh-pages
	git subtree push --prefix dist origin gh-pages
else
	echo "Are you sure? If yes call using \"$0 -f\""
fi

