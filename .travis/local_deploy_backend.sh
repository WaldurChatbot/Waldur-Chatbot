#!/bin/bash

DIRECT="backend"
SCRIPT="Waldur.py"

# we are working on the assumption that the remote server already has cloned this repo
cd Waldur-Chatbot
git checkout master
git pull

# install requirements
sudo pip install -r requirements.txt --upgrade

# kill process if running
[ -f pid ] && kill `cat pid`

# start process
cd ${DIRECT}
nohup python3.5 ${SCRIPT} > /dev/null 2>&1 & echo $! > ../pid
echo "Started" ${DIRECT}/${SCRIPT}

sleep 5

if ps -p `cat ../pid` > /dev/null
then
   echo "`cat ../pid` is running"
   exit 0
else
   echo ${DIRECT}/${SCRIPT} "is not running"
   exit 100
fi
