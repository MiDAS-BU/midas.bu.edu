#!/usr/bin/env bash
# This is to be used only if something is wrong with current gh-pages
# It first deletes current gh-pages branch and then pushing everything anew

USERNAME=dstara
SERVER="csa1.bu.edu"
REMOTESSH="ssh -F /dev/null ${USERNAME}@${SERVER} -o PasswordAuthentication=no"

GREENOK="\033[32mOK!\033[0m"
REDERROR="\033[31mERROR\033[0m"

echo "Remote deploying ..."
REMOTELS=`$REMOTESSH "ls ~/Repos/midas.bu.edu/redeploy.sh"`
REMOTE_RET=$?
if [ ${REMOTE_RET} -eq 255 ]; then
    echo "***************************************************"
    echo -e "$REDERROR: Cannot connect using ${USERNAME}@${SERVER}"
elif [ ${REMOTE_RET} -ne 0 ]; then
    echo "***************************************************"
    echo -e "$REDERROR: Something went wrong when searching MiDAS repo in the remote server"
    echo -e "$REDERROR: Make sure you have MiDAS repo at: ~/Repos/midas.bu.edu in the remote server: $SERVER"
else
    echo "***************************************************"
    echo -e "${GREENOK} Found remote repo. Will try to git pull remotely ..."
    REMOTEGITPULL=`$REMOTESSH "cd ~/Repos/midas.bu.edu/; git pull"`
    if [ "${REMOTEGITPULL}" != "Already up-to-date." ]; then
        echo "***************************************************"
        echo -e "$REDERROR: Remote git pull was not clean (message was: \"$REMOTEGITPULL\")"
    else
        echo "***************************************************"
        echo -e "${GREENOK} Clean remote pull. Redeploying ..."
        echo "**********************"
        REMOTEREDEPLOY=`$REMOTESSH "cd ~/Repos/midas.bu.edu/; git subtree push --prefix website origin gh-pages"`
        echo "**********************"
        echo -e "${GREENOK} Navigate to https://midas.bu.edu to verify the page is working."
    fi
fi
