#!/bin/bash

# Script that is executed by travis.
# Moves remote deploy script to remote machine and executes it

echo "Starting deployment"
# variables in travis
USER=${PRODUSER}
REMOTE=${PRODREMOTE}
KEY=${encrypted_35a0e268d508_key}
IV=${encrypted_35a0e268d508_iv}

# paths
SCRIPT="local_deploy_backend.sh"
ENCRYPTED_KEY=".travis/deploy_rsa.enc"
DECRYPTED_KEY=".travis/deploy_rsa"

echo "Decrypting private key"
openssl aes-256-cbc \
                    -K ${KEY} \
                    -iv ${IV} \
                    -in ${ENCRYPTED_KEY} \
                    -out ${DECRYPTED_KEY} \
                    -d

chmod 600 ${DECRYPTED_KEY}

echo "Moving ${SCRIPT} to remote"
scp -o "StrictHostKeyChecking no" -i ${DECRYPTED_KEY} .travis/${SCRIPT} ${USER}@${REMOTE}:~/

echo "Executing ${SCRIPT} in remote"
ssh -o "StrictHostKeyChecking no" -i ${DECRYPTED_KEY} ${USER}@${REMOTE} ./${SCRIPT}
