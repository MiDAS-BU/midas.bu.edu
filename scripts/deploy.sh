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

# https://unix.stackexchange.com/a/155077/219051
if output=$(git status --porcelain) && [ -z "$output" ]
then
	sed -i "" '/dist/d' ./.gitignore
	git add .
	git commit -m "Edit .gitignore to publish"
	git push origin `git subtree split --prefix dist master`:gh-pages --force
	git reset HEAD~
	git checkout .gitignore
else
	echo "Need clean working directory to publish"
fi

# if [ $? -ne 0 ]; then
# 	echo "Something went wrong"
# 	echo "Re-deploying by force deleting gh-page are and re-creating it."
# 	./scripts/redeploy.sh -f
# fi






