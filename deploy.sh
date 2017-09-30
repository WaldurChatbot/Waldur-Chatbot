#!/bin/bash

echo "Deploying"
# if supplied argument is 'dev', use develop branch
script="./local_deploy.sh"
if [ ! -z $1 ]; then
    if [ $1 = "dev" ]; then
        script="./local_deploy.sh dev"
    fi
fi

echo $script

openssl aes-256-cbc -K $encrypted_5899b1a8b456_key -iv $encrypted_5899b1a8b456_iv -in .travis/travis_deploy_key.enc -out .travis/travis_deploy_key -d
chmod 600 .travis/travis_deploy_key
scp -o "StrictHostKeyChecking no" -i .travis/travis_deploy_key deploy.sh $DEVUSER@$DEVREMOTE:~/
ssh -o "StrictHostKeyChecking no" -i .travis/travis_deploy_key $DEVUSE@$DEVREMOTE './local_deploy.sh dev'
