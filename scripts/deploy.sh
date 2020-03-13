#!/usr/bin/env bash

# if -f supplied, will force-recreate gh-pages branch

set -e

# Ensure that the CWD is set to script's location
cd "${0%/*}"
CWD=$(pwd)
cd ..

#######

echo "Pulling / pushing ... (should pull nothing)"

git pull
git push

echo "Assembling the site..."

./scripts/build.py

echo "Pushing gh-pages..."

# https://stackoverflow.com/a/40178818/1644554
# https://unix.stackexchange.com/a/155077/219051
if output=$(git status --porcelain) && [ -z "$output" ]
then
	if [ $# -eq 1 ] && [ $1 = "-f" ]
	then
		git push origin --delete gh-pages
	fi

	sed -i "" '/dist/d' ./.gitignore
	git add .
	git commit -m "Edit .gitignore to publish"
	git push origin `git subtree split --prefix dist master`:gh-pages --force
	git reset HEAD~
	git checkout .gitignore
	echo "Done!"
else
	echo "Need clean working directory to publish -- WILL NOT PUBLISH!!"
fi

