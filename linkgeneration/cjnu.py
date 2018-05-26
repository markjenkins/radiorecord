from .dategeneration import generate_dates_for_showtime

# not yet live
URLBASE = "http://archive-files.cjnu.ca/"
FILESUFFIX = ".mp3"

def generate_links_for_showtime(
    dayofweek, starttimeofday, lasthour=None, weeksback=None):
    return [
        [ (URLBASE +
           "%(year).4d/" + "%(month).2d/" + "%(day).2d/" +
           "CJNU-" +
           "%(year).4d-" + "%(month).2d-" + "%(day).2d_" +
           "%(starthour).2d-00" +
           FILESUFFIX ) % {
               'year': ephour.year,
               'month': ephour.month,
               'day': ephour.day,
               'starthour': ephour.hour,
           } # end dict fed to string formating
          for ephour in episode] # end inner list comprehension 
        for episode in generate_dates_for_showtime(
            dayofweek, starttimeofday, lasthour=lasthour, weeksback=weeksback)
    ] # end outer list comprehension

