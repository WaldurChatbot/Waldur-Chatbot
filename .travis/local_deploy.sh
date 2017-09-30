#!/bin/bash

# the target should already have cloned this repo
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
sudo pip install -r telegrambot/requirements.txt
sudo pip install -r fleepbot/requirements.txt
sudo pip install -r backend/requirements.txt

# kill all python processes
pkill python3.5

# start processes
cd backend
nohup python3.5 Waldur.py > /dev/null 2>&1 &
echo "Started backend"
cd ../telegrambot
nohup python3.5 telegrambot.py > /dev/null 2>&1 &
echo "Started telegram bot"
cd ../fleepbot
nohup python3.5 fleepbot.py > /dev/null 2>&1 &
echo "Started fleep bot"

exit 0
