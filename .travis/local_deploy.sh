#!/bin/bash

# Script that is started in remote machine
#  - Pulls latest state from repository's master branch
#  - Installs requirements by pip
#  - Starts process in background
#  - Checks if process is still alive 5 seconds after execution

# we are working on the assumption that the remote server already has cloned this repo

# get arguments from command line
NAME=${1}
PATH_TO_SCRIPT=${2}
SCRIPT=${3}

cd ${NAME}
git stash
git checkout master
git pull

# install requirements
sudo pip install -r requirements.txt --upgrade

# kill process if running
[ -f pid ] && kill `cat pid`

# start process and save pid to file 'pid'
cd ${PATH_TO_SCRIPT}
nohup python3.5 ${SCRIPT} > /dev/null 2>&1 & echo $! > ../pid
echo "Started ${PATH_TO_SCRIPT}/${SCRIPT}"

sleep 5

PID=`cat ../pid`

# check if script started
if ps -p ${PID} > /dev/null
then
   echo "${NAME} is running with pid ${PID}"
   exit 0
else
   echo "${NAME} is not running"
   exit 100
fi
