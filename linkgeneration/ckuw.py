from linkgeneration.dategeneration import generate_dates_for_showtime

# example http://ckuw.ca/128/20180523.08.00-09.00.mp3
URLBASE = "http://ckuw.ca/128/"
FILESUFFIX = ".mp3"

def generate_link_for_showtime(ephour):
    return (URLBASE +
            "%(year).4d" + "%(month).2d" + "%(day).2d" + "." +
            "%(starthour).2d.00-" +
            "%(endhour).2d.00" + FILESUFFIX ) % {
                'year': ephour.year,
                'month': ephour.month,
                'day': ephour.day,
                'starthour': ephour.hour,
                'endhour': (ephour.hour+1) % 24
            } # end dict fed to string formating

def generate_links_and_dates_for_showtime(
    dayofweek, starttimeofday, lasthour=None, weeksback=None):
    if lasthour==None:
        lasthour=starttimeofday
    # there's an inner and an outer list comprehension here
    return [ [
        { 'link': generate_link_for_showtime(ephour),
          'hour': ephour.hour,
          'hour-date': ephour.date().isoformat()
        }
                 for ephour in episode]
             for episode in generate_dates_for_showtime(
                dayofweek, starttimeofday,
                lasthour=lasthour, weeksback=weeksback)
        ] # end outer list comprehension

def generate_links_handler(event, context):
    lasthour = None if 'lasthour' not in event['params']['querystring'] else int(event['params']['querystring']['lasthour'])
    weeksback = None if 'weeksback' not in event['params']['querystring'] else int(event['params']['querystring']['weeksback'])
    return generate_links_and_dates_for_showtime( event['params']['querystring']['dayofweek'],
                                        int(event['params']['querystring']['starttimeofday']),
                                        lasthour=lasthour,
                                        weeksback=weeksback)
