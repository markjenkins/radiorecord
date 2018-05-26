#!/usr/bin/env python3

from datetime import date, timedelta

HOURS_PER_DAY=24

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

DEFAULT_WEEKS_BACK = 5

if __name__ == "__main__":
    print( weeks_or_days_date_back(5, date.today() ) )
    print( weeks_or_days_date_back(20, date.today(), 
                                   increment=timedelta(days=1) ) )
    
    print(hours_between_start_and_end_inclusive(6,8) )
    print(hours_between_start_and_end_inclusive(23,4) )
    print(hours_between_start_and_end_inclusive(23,0) )
    print(hours_between_start_and_end_inclusive(10,4) )
