#!/usr/bin/env python3

from datetime import date, timedelta

def weeks_or_days_date_back(
        num_days_weeks, most_recent_date,
        increment=timedelta(days=7) ):
    return [
        most_recent_date - increment*i
        for i in range(num_days_weeks)
        ]

DEFAULT_WEEKS_BACK = 5

if __name__ == "__main__":
    print( weeks_or_days_date_back(5, date.today() ) )
    print( weeks_or_days_date_back(20, date.today(), 
                                   increment=timedelta(days=1) ) )
