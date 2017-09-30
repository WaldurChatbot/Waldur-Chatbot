#!/usr/bin/env bash

# if supplied argument is 'dev', use develop branch
script = "./local_deploy.sh"
if [ ! -z $1 ]; then
    if [ $1 == "dev" ]; then
        script = "./local_deploy.sh dev"
    fi
fi

echo "ok"
echo $script
exit 0

#openssl aes-256-cbc -K $encrypted_5899b1a8b456_key -iv $encrypted_5899b1a8b456_iv -in .travis/travis_deploy_key.enc -out travis_deploy_key -d
#scp deploy.sh $DEVUSER@$DEVREMOTE:~/
#ssh $DEVUSE@$DEVREMOTE $script