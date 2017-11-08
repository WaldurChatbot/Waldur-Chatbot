#!/bin/bash

# Script that is executed by travis.
# Moves remote deploy script to remote machine and executes it

echo "Starting deployment"
# encrypted variables in travis
USER=${PRODUSER}
REMOTE=${PRODREMOTE}
KEY=${encrypted_35a0e268d508_key}
IV=${encrypted_35a0e268d508_iv}

# variables in .travis.yml
SCRIPT=${LOCAL_DEPLOY_SCRIPT}
ENCRYPTED_KEY=${TRAVIS_DIR}"deploy_rsa.enc"
DECRYPTED_KEY=${TRAVIS_DIR}"deploy_rsa"

# general travis variable
BRANCH=${TRAVIS_BRANCH}
CLONE_URL="git@github.com:"${TRAVIS_REPO_SLUG}

echo "Decrypting private key"
openssl aes-256-cbc \
                    -K ${KEY} \
                    -iv ${IV} \
                    -in ${ENCRYPTED_KEY} \
                    -out ${DECRYPTED_KEY} \
                    -d

chmod 600 ${DECRYPTED_KEY}

echo "Moving ${SCRIPT} to remote"
scp \
    -o "StrictHostKeyChecking no" \
    -i ${DECRYPTED_KEY} \
    ${TRAVIS_DIR}${SCRIPT} \
    ${USER}@${REMOTE}:~/

echo "Executing ${SCRIPT} in remote"
ssh \
    -o "StrictHostKeyChecking no" \
    -i ${DECRYPTED_KEY} \
    ${USER}@${REMOTE} \
    ./${SCRIPT} ${NAME} ${PATH_TO_RUN_SCRIPT} ${RUN_SCRIPT} ${BRANCH} ${CLONE_URL}
