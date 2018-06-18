#!/usr/bin/env python3

from linkgeneration.ckuw import generate_links_and_dates_for_showtime

for episode in generate_links_and_dates_for_showtime('tuesday', 8):
    print()
    for hourseg in episode:
        print(hourseg)
