#!/bin/sh

LOG=/var/log/reupload_server.log

echo -n "starting reupload server at " >> $LOG
date >> $LOG
/usr/local/bin/reupload_server.py >> $LOG 2>&1
echo -n "reupload server stopped at " >> $LOG
date >> $LOG
