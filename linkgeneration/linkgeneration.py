#!/usr/bin/env python3

from datetime import date, datetime, timedelta

DEFAULT_WEEKS_BACK = 5
HOURS_PER_DAY=24
NUMBER_OF_DAYS_IN_WEEK = 7

def weeks_or_days_date_back(
        num_days_weeks, most_recent_date,
        increment=timedelta(days=7) ):
    return [
        most_recent_date - increment*i
        for i in range(num_days_weeks)
        ]

def valid_hour(hour):
    return 0<=hour<=(HOURS_PER_DAY-1) # (0-23 inclusive)

def hours_between_start_and_end_inclusive(start_hour, last_hour):
    if not (valid_hour(start_hour) and valid_hour(last_hour)):
        raise ValueError("invalid start or end hour")
    
    return (last_hour - start_hour) % 24 + 1

def date_as_hour_start_datetime(relevant_date, relevant_hour):
    return datetime(
        year=relevant_date.year,
        month=relevant_date.month,
        day=relevant_date.day,
        hour=relevant_hour)

def dates_with_included_start_and_last_hours(
        dates_to_work_through, start_hour, last_hour):
    hour_deltas = [ 
        timedelta(hours=i)
        for i in range(hours_between_start_and_end_inclusive(start_hour, 
                                                             last_hour) )
        ]

    return [
        [ date_as_hour_start_datetime(relevant_date, start_hour)+hour_delta
          for hour_delta in hour_deltas ]
        for relevant_date in dates_to_work_through
        ]

weekday_map = {
    0: 'monday',
    1: 'tuesday',
    2: 'wednesday',
    2: 'thursday',
    2: 'friday',
    5: 'saturday',
    6: 'sunday',
    }

weekday_keys = list(weekday_map.keys())
min_weekday = min(weekday_keys)
max_weekday = max(weekday_keys)

def valid_weekday(weekday):
    return min_weekday<=weekday<=max_weekday

def most_recent_date_w_day_of_week_prior_to(
        weekday, start_hour, datetime_to_compare):
    if not valid_weekday(weekday):
        raise ValueError("not a valid week day")
    
    recent_day = datetime_to_compare.weekday()
    # I originally used iteration to find the most recent date
    # with a matching day of the week
    #for i in range(NUMBER_OF_DAYS_IN_WEEK):
    #    if recent_day == weekday:
    #        break

        # we can use modular arithmatic if these assumptions hold
    #    assert(min_weekday==0)
    #    assert(max_weekday==6)
    #    recent_day = (recent_day-1) % NUMBER_OF_DAYS_IN_WEEK
    #found_date_near_comparetime = datetime_to_compare + timedelta(days=-i)

    # but then I found I could do it arithmetically
    num_days_prior = (recent_day - weekday) % NUMBER_OF_DAYS_IN_WEEK
    found_date_near_comparetime = \
        datetime_to_compare + timedelta(days=-num_days_prior)
    
    # use the provided start_hour
    found_datetime = datetime( year=found_date_near_comparetime.year,
                               month=found_date_near_comparetime.month,
                               day=found_date_near_comparetime.day,
                               hour=start_hour )
    assert( found_datetime.weekday() == weekday )

    if found_datetime <= datetime_to_compare:
        return found_datetime
    else:
        return_datetime =  found_datetime - timedelta(7)
        assert( return_datetime < datetime_to_compare)
        return return_datetime

if __name__ == "__main__":
    print( weeks_or_days_date_back(5, date.today() ) )
    print( weeks_or_days_date_back(20, date.today(), 
                                   increment=timedelta(days=1) ) )
    
    print(hours_between_start_and_end_inclusive(6,8) )
    print(hours_between_start_and_end_inclusive(23,4) )
    print(hours_between_start_and_end_inclusive(23,0) )
    print(hours_between_start_and_end_inclusive(10,4) )

    print( dates_with_included_start_and_last_hours(
        weeks_or_days_date_back(5, date.today()),
        2,3
    ) )

    print( dates_with_included_start_and_last_hours(
        weeks_or_days_date_back(5, date.today()),
        23,2
    ) )

    print(
        most_recent_date_w_day_of_week_prior_to(
            6, 10, datetime(2018,5,26, 9)
        ) )
