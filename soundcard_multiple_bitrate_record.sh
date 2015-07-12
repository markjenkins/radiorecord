#!/bin/bash

ARCHIVE_DIR=`pwd`

encode () {
    _bitrate=$1
    _mode=$2
    _extra_flags=$3
    lame -r --bitwidth 16 -s 44.1 $_extra_flags -m $_mode -b $_bitrate --cbr - -
}

log () {
    _bitrate=$1
    cronolog -H $ARCHIVE_DIR/$_bitrate/current.mp3 \
-p "2 hours" $ARCHIVE_DIR/$_bitrate/%Y-%m-%d/%s.mp3
}


REALTIME_FLAGS='-B rt -r'

# -a inserted for mono mixdown to signal that original audio is in stereo
ecasound  -q -C  $REALTIME_FLAGS -b 4096 -i alsa -o stdout | \
tee >(encode 24 m -a | log 24) | \
encode 128 j | log 128


