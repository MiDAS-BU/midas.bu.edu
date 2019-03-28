#!/usr/bin/env bash
# This is to be used only if something is wrong with current gh-pages
# It first deletes current gh-pages branch and then pushing everything anew

git push origin --delete gh-pages

git subtree push --prefix website origin gh-pages
