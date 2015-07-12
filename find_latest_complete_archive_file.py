#!/usr/bin/env python

# find_latest_complete_archive_file.py
# Copyright (C) 2011 ParIT Worker Co-operative <transparency@parit.ca>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Author(s): Mark Jenkins <mark@parit.ca>

# Identifies the latest complete archive file matching
# ????-??-??/*.mp3 under a target directory by going under the big assumption
# the the latest complete one is the second newest one by file name in reverse
# sort order -- the deeper assumption here is that the newest one is
# incomplete and in-progress.
#
# result is printed to stdout
#
# This also assumes both the file and directory names reflect age in reverse
# sort order.
#
# Examples:
# latest_archive_test/2011-01-02/223.mp3
# latest_archive_test/2011-01-02/222.mp3
# latest_archive_test/2011-01-01/123.mp3
# the middle one is picked
#
# The first argument specifies the target directory to look under

from sys import argv
from itertools import islice
from glob import iglob
from os.path import join as path_join
from os import listdir

def flatten_nested_iters(iters):
    # there has got to be a substitute for this...
    for inner_iter in iters:
        for blob in inner_iter:
            yield blob

def find_2nd_newest_archive_file(top_level_dir):
    return islice(flatten_nested_iters( 
            islice(sorted(iglob(path_join(archive_dir, '*.mp3')), reverse=True),
                   0, 2) # first 1 or 2 files        

            # look at the one or two archive directories with the newest
            # dates in thier name
            for archive_dir in islice(sorted(
                    iglob(path_join(top_level_dir, '????-??-??'))
                    , reverse=True), # reversed for newest
                                      0, 2)  # islice arguments)
            # arguments to outer islice mean get second in sequenece
            ), 1, 2).next()

if __name__ == "__main__":
    print find_2nd_newest_archive_file(argv[1])
