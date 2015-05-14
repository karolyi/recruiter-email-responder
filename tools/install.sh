#!/usr/bin/env bash

PROJECT_DIR=$(cd $(dirname ${BASH_SOURCE[0]});cd ..;pwd)

cd $PROJECT_DIR

pyvenv virtualenv
source virtualenv/bin/activate

pip install -r requirements.txt
