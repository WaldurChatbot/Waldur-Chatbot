#!/bin/bash

# the target should already have cloned this repo
# check if repo is cloned, if is not, clone
cd Waldur-Chatbot

# if supplied argument is 'dev', use develop branch
if [ ! -z $1 ]; then
    if [ $1 == "dev" ]; then
        git checkout develop
    else
        git checkout master
    fi
else
    git checkout master
fi

git pull

# install requirements
sudo pip install -r requirements.txt

# kill all python processes
pkill python3.5

# start processes
cd backend
nohup python3.5 Waldur.py > /dev/null 2>&1 &
echo "Started backend"

exit 0
