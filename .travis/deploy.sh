#!/bin/bash

# Script that is executed by travis.
# Moves remote deploy script to remote machine and executes it

echo "Starting deployment"

# variables in .travis.yml
SCRIPT=${LOCAL_DEPLOY_SCRIPT}
ENCRYPTED_KEY=${TRAVIS_DIR}"deploy_rsa.enc"
DECRYPTED_KEY=${TRAVIS_DIR}"deploy_rsa"

# general travis variable
BRANCH=${TRAVIS_BRANCH}
CLONE_URL="https://github.com/"${TRAVIS_REPO_SLUG}

echo "SCRIPT=${SCRIPT}"
echo "BRANCH=${BRANCH}"
echo "CLONE_URL=${CLONE_URL}"

# encrypted variables in travis
if [ "${BRANCH}" == "master" ]
then
    USER=${PRODUSER}
    REMOTE=${PRODREMOTE}
elif [ "${BRANCH}" == "develop" ]
then
    USER=${DEVUSER}
    REMOTE=${DEVREMOTE}
else
    exit 1
fi
KEY=${encrypted_35a0e268d508_key}
IV=${encrypted_35a0e268d508_iv}

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