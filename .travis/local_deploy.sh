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
BRANCH=${4}
CLONE_URL=${5}

hostname
echo "NAME=${NAME}"
echo "PATH_TO_SCRIPT=${PATH_TO_SCRIPT}"
echo "SCRIPT=${SCRIPT}"
echo "BRANCH=${BRANCH}"
echo "CLONE_URL=${CLONE_URL}"

# install stuff if necessary
if ! command -v git || ! command -v pip3
then
    sudo apt-get update
fi

if ! command -v git
then
    sudo apt-get install -y git
fi

if ! command -v pip3
then
    sudo apt-get install -y python3-pip
fi

# if dir exists, we assume the repo is already cloned
if cd ${NAME}
then
    git stash
    git checkout ${BRANCH}
    git pull
else
    git clone -b ${BRANCH} ${CLONE_URL}
    cd ${NAME}
fi

# install requirements
sudo pip3 install -r requirements.txt --upgrade

# kill process if running
[ -f pid ] && kill `cat pid`

# start process and save pid to file 'pid'
cd ${PATH_TO_SCRIPT}
nohup python3.5 ${SCRIPT} > raw.out 2>&1 & echo $! > ../pid
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
