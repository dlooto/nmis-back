#!/bin/bash
set -e
TIMEOUT=300   #to solve upload app package timeout issue

cd /home/deploy/nmis/prod/nmis-back/apps

# activate the virtualenv
workon nmis

# changed:  --bind 0.0.0.0:8002 to --bind 127.0.0.1:8002, forbid 8002 port access
exec gunicorn wsgi -w 2 \
    --bind 127.0.0.1:8002 \
    --settings settings.local \
    --user deploy --group deploy \
    --timeout $TIMEOUT \
    --log-level info
