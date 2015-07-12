#!/bin/bash

# arguments
# $1 -> uploadhost
# $2 -> file_orig_path
# $3 -> username
# $4 -> keyfile

KEY=$4

UPLOADHOST=$1

FILE_ORIG_PATH=$2
FILE_DAY_DIR_FULL=`/usr/bin/dirname $FILE_ORIG_PATH`
FILE_DAY_DIR=`/usr/bin/basename $FILE_DAY_DIR_FULL`
SPEED_FULL=`/usr/bin/dirname $FILE_DAY_DIR_FULL`
SPEED=`/usr/bin/basename $SPEED_FULL`
FILENAME=`/usr/bin/basename $FILE_ORIG_PATH`

/usr/bin/sftp -b - -oIdentityFile=$KEY \
$3@$UPLOADHOST <<EOF > /dev/null 2>&1
cd archives
cd $SPEED
mkdir $FILE_DAY_DIR
quit
EOF

echo /usr/bin/sftp -b - -oIdentityFile=$KEY \
$3@$UPLOADHOST <<EOF  > /dev/null 2>&1
cd archives
cd $SPEED
put $FILE_ORIG_PATH $FILE_DAY_DIR/$FILENAME
quit
EOF
