TwistedSchedule
===============

This package is designed to present a helpful interface for performing
recurring calls of a function at long and irregular intervals. Twisted's
`LoopingCall` and time-based deferring methods take seconds as the time
argument, making writing schedules like "Every Monday at 8am and every Friday
at 5pm" difficult.

The `cron` decorator provided by this package takes crontab-like schedules and
takes care of scheduling the function calls within the Twisted reactor at
predefined intervals.

## Crontab Schedules

Currently, support is only for hours, minutes and seconds, but I am planning on
including support for days of week.

Schedules are either given as sequencesor as steps. Sequences are
comma-separated lists of values:

```
1,2,3,10,30
```
ranges:

```
1-10 => yields 1,2,3,4,5,6,7,8,9,10
```
or combinations of both:

```
1,5,10-15,30 => yields 1,5,10,11,12,13,14,15,30
```

Steps yield sequences of multiples:

```
*/5 => yields 0, 5, 10, 15, etc
```

When you create a schedule, you specify the crontab string for each unit of time, e.g.

```
@cron(hour='*/2',minute='*/5')
```

which takes care of determining the valid range of values across that
particular unit of time: Hours are 0-23, minutes are 0-59, seconds are 0-59.

## How to Install

```
git clone https://github.com/SoftwareDefinedBuildings/TwistedSchedule
cd TwistedSchedule
sudo python setup.py install
```

## How to Use

```
from twistedschedule.cron import cron

@cron(hour='*/2')
def run_every_two_hours():
    print 'This runs at midnight, 2am, 4am, etc'

@cron(minute='1-5')
def run_first_5min():
    print 'This runs the every minute for the first 5 minutes of every hour'
```
