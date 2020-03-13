#!/usr/bin/env bash

# Ensure that the CWD is set to script's location
cd "${0%/*}"
CWD=$(pwd)
cd ..

#######

echo "Pulling ... (should pull nothing)"

git pull

if [ $? -ne 0 ]; then
	echo "Something went wrong with pulling, please investigate. Exiting ..."
	exit
fi


git subtree push --prefix dist origin gh-pages

if [ $? -ne 0 ]; then
	echo "Something went wrong"
	echo "Re-deploying by force deleting gh-page are and re-creating it."
	./scripts/redeploy.sh -f
fi






