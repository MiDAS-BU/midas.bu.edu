#!/usr/bin/env bash

git subtree push --prefix website origin gh-pages

if [ $? -ne 0 ]; then
    echo "Something went wrong"
    echo "Re-deploying by force deleting gh-page are and re-creating it."
    ./redeploy.sh -f
fi






