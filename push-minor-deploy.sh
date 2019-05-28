#!/usr/bin/env bash
# This scripts commits a minor change and deploys

git pull 
if [ $? -ne 0 ]; then
    echo "Could not pull. Exiting!"
    exit
fi

git add -u && git commit -m "minor"
if [ $? -ne 0 ]; then
    echo "Could not commit the minor change. Please check whether your repository tree is consistent. Existing!"
    exit
fi

git push
if [ $? -ne 0 ]; then
    echo "Could not push. Please check whether your repository tree is consistent. Existing!"
    exit
fi

if [ $? -eq 0 ]; then
    ./deploy.sh
fi



