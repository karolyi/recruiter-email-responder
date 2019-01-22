#!/usr/bin/env sh

PROJECT_DIR=$(cd $(dirname $(readlink -f "$0"));pwd)

cd $PROJECT_DIR

. venv/bin/activate

exec python email-responder.py
