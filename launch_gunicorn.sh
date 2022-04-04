#!/bin/bash

. ~/pyenvs/pyenv1/bin/activate

pushd ~/web_server/ > /dev/null
gunicorn -c gunicorn_conf.py main:app

popd
deactivate
