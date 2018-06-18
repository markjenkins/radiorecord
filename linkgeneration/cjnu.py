from linkgeneration.dategeneration import generate_dates_for_showtime

# not yet live
URLBASE = "https://cjnu-archive-files.s3.us-east-2.amazonaws.com/"
FILESUFFIX = ".mp3"

month_table = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
    }

def generate_link_for_showtime(ephour):
    return (URLBASE +
           "%(year).4d/" + "%(month).2d+%(month_name)s/" + "%(day).2d/" +
           "CJNU_" +
           "%(year).4d-" + "%(month).2d-" + "%(day).2d_" +
           "%(starthour).2d-00" +
           FILESUFFIX ) % {
                'year': ephour.year,
                'month': ephour.month,
                'month_name': month_table[ephour.month],
                'day': ephour.day,
                'starthour': ephour.hour,
                'endhour': (ephour.hour+1) % 24
            } # end dict fed to string formating

def generate_links_and_dates_for_showtime(
    dayofweek, starttimeofday, lasthour=None, weeksback=None):
    if lasthour==None:
        lasthour=starttimeofday
    # there's an inner and an outer list comprehension here
    return [
        {
            'segments': [ {
                'link': generate_link_for_showtime(ephour),
                'hour': ephour.hour,
                'hour-date': ephour.date().isoformat(),
                'hour-count': i+1
            }
            for i,ephour in enumerate(episode)
            ], # end segments list comprehension

            'date-pretty': episode[0].strftime("%A %B %d, %Y"),
            'first-hour':
                str(episode[0].hour % 12
                    if episode[0].hour not in (0,12) else 12) + " " +
                episode[0].strftime("%p").lower() # am or pm
        }
        for episode in generate_dates_for_showtime(
            dayofweek, starttimeofday,
            lasthour=lasthour, weeksback=weeksback)
    ] # end outer list comprehension

def generate_links_handler(event, context):
    lasthour = None if 'lasthour' not in event else int(event['lasthour'])
    weeksback = None if 'weeksback' not in event else int(event['weeksback'])
    return generate_links_and_dates_for_showtime(
        event['dayofweek'],
        int(event['starttimeofday']),
        lasthour=lasthour,
        weeksback=weeksback )
