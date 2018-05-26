from .dategeneration import generate_dates_for_showtime

# example http://ckuw.ca/128/20180523.08.00-09.00.mp3
URLBASE = "http://ckuw.ca/128/"
FILESUFFIX = ".mp3"

def generate_links_for_showtime(
    dayofweek, starttimeofday, lasthour=None, weeksback=None):
    if lasthour==None:
        lasthour=starttimeofday
    return [
        [ (URLBASE +
           "%(year).4d" + "%(month).2d" + "%(day).2d" + "." +
           "%(starthour).2d.00-" +
           "%(endhour).2d.00" + FILESUFFIX ) % {
               'year': ephour.year,
               'month': ephour.month,
               'day': ephour.day,
               'starthour': ephour.hour,
               'endhour': (lasthour+1) % 24
               } # end dict fed to string formating
          for ephour in episode] # end inner list comprehension 
        for episode in generate_dates_for_showtime(
                dayofweek, starttimeofday,
                lasthour=lasthour, weeksback=weeksback)
        ] # end outer list comprehension

