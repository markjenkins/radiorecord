#!/usr/bin/env python3

from linkgeneration.cjnu import generate_links_for_showtime

for episode in generate_links_for_showtime('tuesday', 8):
    print()
    print( '\n'.join(episode) )
