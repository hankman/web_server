#!/bin/bash

. ~/pyenvs/pyenv1/bin/activate

pushd ~/web_server/
gunicorn -c gunicorn_conf.py main:app

popd
deactivate
