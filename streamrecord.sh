#/bin/sh

# requires:
# wget http://www.gnu.org/software/wget/
# cronolog https://github.com/xakz/cronolog
#          https://packages.debian.org/jessie/cronolog

# First argument is stream to record
# Example ./streamrecord.sh http://stream-dc1.radioparadise.com:80/mp3-128
# Needs to be the url to the actual stream, not a m3u or pls file that lists such a thing
STREAM_URL=$1

ARCHIVE_DIR=`pwd`

while true; do \
wget -q -O - $STREAM_URL | \
cronolog -H $ARCHIVE_DIR/current.mp3 \
-p "2 hours" $ARCHIVE_DIR/%Y-%m-%d/%s.mp3

sleep 1s
done
