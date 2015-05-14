#!/usr/bin/env bash

PROJECT_DIR=$(cd $(dirname ${BASH_SOURCE[0]});pwd)

cd $PROJECT_DIR

source virtualenv/bin/activate

exec python3 email-responder.py
