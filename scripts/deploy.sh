#!/usr/bin/env bash

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
	./redeploy.sh -f
fi






