---
title: "Working with Dates and Times"
language: python
difficulty: intermediate
prerequisites: ["Modules and Packages", "Error Handling"]
keywords: [datetime, date, time, timedelta, timezone, formatting, parsing]
---

# Learning Objectives

- Work with dates and times using the `datetime` module
- Create, format, and parse dates
- Perform date arithmetic with `timedelta`
- Understand timezones
- Format dates for display
- Parse dates from strings

# Prerequisites

- Modules and Packages
- Error Handling

# Introduction

Working with dates and times is common in programming. Python's `datetime` module provides comprehensive tools for handling dates, times, and time intervals. Understanding date/time operations is essential for logging, scheduling, data analysis, and many other applications.

# Core Concepts

## The datetime Module

Import the datetime module:

```python
from datetime import datetime, date, time, timedelta
```

## Creating Dates and Times

### Current Date and Time

```python
# Current date and time
now = datetime.now()
print(now)  # Output: 2024-01-15 14:30:45.123456

# Current date only
today = date.today()
print(today)  # Output: 2024-01-15

# Current time only
current_time = datetime.now().time()
print(current_time)  # Output: 14:30:45.123456
```

### Specific Dates and Times

```python
# Create specific date
birthday = date(1990, 5, 15)
print(birthday)  # Output: 1990-05-15

# Create specific datetime
event = datetime(2024, 12, 25, 10, 30, 0)
print(event)  # Output: 2024-12-25 10:30:00

# Create time
meeting_time = time(14, 30, 0)
print(meeting_time)  # Output: 14:30:00
```

## Formatting Dates

Convert dates to strings with specific formats:

```python
from datetime import datetime

now = datetime.now()

# Format as string
formatted = now.strftime("%Y-%m-%d %H:%M:%S")
print(formatted)  # Output: 2024-01-15 14:30:45

# Common format codes
print(now.strftime("%B %d, %Y"))      # January 15, 2024
print(now.strftime("%A, %B %d"))      # Monday, January 15
print(now.strftime("%I:%M %p"))       # 02:30 PM
```

Common format codes:

- `%Y` - Year (4 digits)
- `%m` - Month (01-12)
- `%d` - Day (01-31)
- `%H` - Hour (00-23)
- `%M` - Minute (00-59)
- `%S` - Second (00-59)
- `%A` - Weekday name
- `%B` - Month name

## Parsing Dates

Convert strings to datetime objects:

```python
from datetime import datetime

# Parse from string
date_string = "2024-01-15 14:30:00"
parsed = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
print(parsed)  # Output: 2024-01-15 14:30:00
```

## Date Arithmetic

Use `timedelta` for date calculations:

```python
from datetime import datetime, timedelta

today = datetime.now()

# Add days
future = today + timedelta(days=7)
print(future)  # 7 days from now

# Subtract days
past = today - timedelta(days=30)
print(past)  # 30 days ago

# Add weeks, hours, minutes
future = today + timedelta(weeks=2, hours=5, minutes=30)
print(future)

# Calculate difference
date1 = datetime(2024, 1, 1)
date2 = datetime(2024, 1, 15)
difference = date2 - date1
print(difference.days)  # Output: 14
```

## Working with Timezones

```python
from datetime import datetime, timezone, timedelta

# UTC time
utc_now = datetime.now(timezone.utc)
print(utc_now)  # Output: 2024-01-15 14:30:45+00:00

# Create timezone
eastern = timezone(timedelta(hours=-5))
eastern_time = datetime.now(eastern)
print(eastern_time)  # Output: 2024-01-15 09:30:45-05:00

# Convert between timezones
utc_time = datetime.now(timezone.utc)
eastern = timezone(timedelta(hours=-5))
eastern_time = utc_time.astimezone(eastern)
```

## Extracting Components

```python
from datetime import datetime

now = datetime.now()

print(now.year)    # 2024
print(now.month)   # 1
print(now.day)     # 15
print(now.hour)    # 14
print(now.minute)  # 30
print(now.second)  # 45
print(now.weekday())  # 0-6 (Monday is 0)
```

## Comparing Dates

```python
from datetime import datetime

date1 = datetime(2024, 1, 1)
date2 = datetime(2024, 1, 15)

print(date1 < date2)   # True
print(date1 > date2)   # False
print(date1 == date2)  # False
```

# Common Mistakes

- **Confusing `datetime` and `date`**: `datetime` includes time, `date` doesn't
- **Wrong format string**: Format string must match the date string exactly
- **Timezone confusion**: Be aware of timezone issues when working with times
- **Not handling parsing errors**: `strptime` raises `ValueError` if format doesn't match
- **Mutable datetime objects**: Datetime objects are immutable

# Practice Exercises

1. Get the current date and time and format it as "January 15, 2024 at 2:30 PM".
2. Calculate how many days until your next birthday.
3. Parse a date string "2024-12-25" and format it as "December 25, 2024".
4. Create a function that calculates the age in days between two dates.
5. Get the current time in UTC and convert it to a different timezone.

Example solution for exercise 2:

```python
from datetime import date, datetime

def days_until_birthday(birth_month, birth_day):
    today = date.today()
    this_year_birthday = date(today.year, birth_month, birth_day)

    if this_year_birthday < today:
        # Birthday already passed this year
        next_birthday = date(today.year + 1, birth_month, birth_day)
    else:
        next_birthday = this_year_birthday

    return (next_birthday - today).days

days = days_until_birthday(5, 15)
print(f"Days until birthday: {days}")
```

# Key Takeaways

- Use `datetime` module for date and time operations
- `datetime.now()` gets current date and time
- Use `strftime()` to format dates as strings
- Use `strptime()` to parse strings into datetime objects
- Use `timedelta` for date arithmetic (adding/subtracting time)
- Be aware of timezone issues when working with times
- Datetime objects are immutable - operations return new objects

# Related Topics

- Modules and Packages (Python Intermediate #5)
- Error Handling (Python Intermediate #3)
- String Formatting (Python Beginner #8)
