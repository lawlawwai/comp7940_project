#!/bin/sh

SECRET_KEY_PASSWORD=$1
# Decrypt the file
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$SECRET_KEY_PASSWORD" \
--output ./firebase-key.json firebase-key.json.gpg