#!/bin/bash

# the target should already have cloned this repo
# todo check if repo is cloned, if is not, clone
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
sudo pip install -r requirements.txt --upgrade

# kill backend if running
[ -f pid ] && kill `cat pid`

# start processes
cd backend
nohup python3.5 Waldur.py > /dev/null 2>&1 & echo $! > ../pid
echo "Started backend"

sleep 5

if ps -p `cat pid` > /dev/null
then
   echo "`cat pid` is running"
   exit 0
else
   echo "Backend is not running"
   exit 100
fi
