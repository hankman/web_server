#!/bin/bash

source /home/cfan/pyenvs/pyenv38/bin/activate

pushd /home/cfan/web_server/ > /dev/null
gunicorn -c gunicorn_conf.py main:app

popd
deactivate
