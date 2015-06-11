#!/usr/bin/env python

# cleanup_oldest_days_in_archive.py
# Copyright (C) 2006,2015 ParIT Worker Co-operative <paritinfo@parit.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Author(s): Mark Jenkins <mark@parit.ca>

# Originally developed for CKUW radio in Winnipeg

# Cleans up the oldest days in a directory based archiving system
# that has YYYY-MM-dd (year/month/day) formatted directories
# To use, configure the two variables below

# you probably want to change this to an absolute path
archive_directory_prefix = "./"

# sub-directories in the above path, used for example at CKUW to clean a 
# 128 and 64kbit audio archive
archive_directories = ("subdir1", "subdir2")


from os import listdir, stat, remove
from sys import stderr
from itertools import dropwhile
import re
from datetime import timedelta, datetime
from shutil import rmtree
from os.path import join

# This is a regular expression that matches archive directories for specific
# days. The format is yyyy-mm-dd . (year, month, day)
# This regular expression will also match nonsense dates like
# 9999-99-99, but I don't care, as it's good enough for the purpose it's
# surving.
# It also fails to match possible future dates like 99999-12-30 because I
# really don't care about the Y10K bug.
#
# For any computer archeologiests who happen to be reading this and scratching
# thier head, these statements written in 2006 when life expectancies in the
# wealthiest places on earth were about 86 years, and real, working,
# turing complete computers (with finite memories) had only existed for about
# 60 years.
#
# Exercise to reader: Change this regular expression to fix the above bugs
day_directory_pattern = re.compile(r"[0-9]{4}-[01][0-9]-[0-3][0-9]")



def filter_list_with_regex(list_to_filter, regex):
    """Filteres a list with a regular expression

    Elements that match the expression (using regex.search) are included
    in the returned list, elements that don't match are excluded
    """
    # I love list comprehensions
    return [ list_match.string
             for list_match in [regex.search(list_item)
                                for list_item in list_to_filter]
             if list_match != None ]

def filter_directory_listing_with_regex(directory, regex):
    return filter_list_with_regex( listdir(directory), regex )

def main():
    for archive_directory in archive_directories:

        full_path_to_archive_directory = join(archive_directory_prefix,
                                              archive_directory )

        # We use the regular expression for day directories to filter out
        # any files or directories in
        # archive_directory_prefix/archive_directory that are not directories
        # for a specific day
        day_directories = filter_directory_listing_with_regex(
            full_path_to_archive_directory,
            day_directory_pattern )

        if len(day_directories) > 0: # do nothing if there are not matches
            # Get the oldest day, this works because of the date format being
            # used. If the date format changes you'll need to change this.
            oldest_day = min(day_directories)

            # Delete the oldest day directory.
            rmtree( join(full_path_to_archive_directory, oldest_day) )

if __name__ == "__main__":
    main()
