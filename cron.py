import re
import datetime
from itertools import cycle
from twisted.internet import reactor, defer
from twisted.internet.task import LoopingCall, deferLater

class CronSchedule(object):

    SECOND_RANGE = range(0,60)
    MINUTE_RANGE = range(0,60)
    HOUR_RANGE = range(0,24)
    DAY_OF_WEEK_RANGE = range(0,7) #Sunday = 0, Monday = 1, ..., Saturday = 6
    TIMEUNITS = {
        'second': SECOND_RANGE,
        'minute': MINUTE_RANGE,
        'hour': HOUR_RANGE,
        'day_of_week': DAY_OF_WEEK_RANGE
    }
    _seq = re.compile(r'(\d+(-\d+)?)(,\d+(-\d+)?)*')
    _step = re.compile(r'\*/\d+')
    _numbers = re.compile(r'\d+')
    _invalidchars = re.compile(r'[^0-9-*/,]')

    def __init__(self, second=None, minute=None, hour=None, day_of_week=None):
        """
        Based on cron-like schedule passed into the constructor, constructs an internal
        iterator that yields seconds until the next calltime. For use with deferLater.

        Each of the arguments to CronSchedule will either be a string or an integer.
        Integers are easy.
        Strings will have the following features: 
            */N -- every timestep divisible by N
            x,y,a-d -- at timesteps x and y as well as every timestep from a to d
        """
        self._second = self.generate('second', second)
        self._minute = self.generate('minute', minute)
        self._hour = self.generate('hour', hour)
        self._day_of_week = self.generate('day_of_week', day_of_week)
        print "second",self._second
        print "minute",self._minute
        print "hour",self._hour
        print "day_of_week",self._day_of_week
        if not (self._second or self._minute or self._hour or self._day_of_week):
            raise ValueError("CronSchedule must be instantiated with at least one timestep")
        self.current = datetime.datetime.now()

    def generate(self, timeunit, cronstring):
        if not cronstring: return None
        assert self._is_valid_chars(cronstring), "{0} contains invalid cron characters".format(cronstring)
        self._check_range(timeunit, cronstring)
        return self._parse_cronstring(timeunit, cronstring)

    def _get_closest(self, value, values):
        """
        Given a value [value] and a list of values [values],
        returns the value from [values] that is > [value]. If
        no such values exist, returns the first item of [values].

        Assumes [values] is sorted in ascending order
        """
        upper = filter(lambda x: x > value, values)
        if len(upper):
            return upper[0]
        else:
            return values[0]

    def next(self):
        """
        Given the current time, generate the datetime object of the next calltime
        according to the cron schedule.

        *default to 0 instead of None on generate()?

        - if there is a second schedule, get the next closest scheduled second, otherwise
          the scheduled second is 0
        - use above second as the second step. if the next second step is < scheduled, then 
          we'll need to increment the minute
        - get closest scheduled minute. if there is a second schedule, this is the current minute
          unless we have the increment flag from above. If there is no second schedule, then this
          should be the next minute step. If there is no minute schedule, this is 0. If the
          next minute step is < the current scheduled step, then increment hour
        - get closest scheduled hour. if there is a minute schedule, this is the current hour
          unless we have the increment flag from above. If there is no minute schedule, then this
          is the next hour step. If there is no hour schedule, then this is 0.
        """
        self.current = datetime.datetime.now()
        nexttime = self.current
        increment_minute = False
        increment_hour = False
        second = 0
        minute = self.current.minute
        hour = self.current.hour
        print '-'*20
        if self._second:
            print 'have second schedule'
            second = self._get_closest(self.current.second, self._second)
            print 'next scheduled second:',second
            next_second = self._get_closest(second, self._second)
            print 'next next sched second:',next_second
            if second == self._second[0]:
                print 'increment minute!'
                increment_minute = True

        if self._minute:
            print 'have minute schedule'
            if self._second:
                minute = self.current.minute + 1*increment_minute
            else:
                minute = self._get_closest(self.current.minute, self._minute)
            print 'next sched min:', minute
            next_minute = self._get_closest(minute, self._minute)
            print 'next next sched min:',next_minute
            if minute == self._minute[0]:
                print 'increment hour!'
                increment_hour = True

        if self._hour:
            if self._minute:
                hour = self.current.hour + 1*increment_hour
            else:
                hour = self._get_closest(self.current.hour, self._hour)
            next_hour = self._get_closest(hour, self._hour)
            print 'hour',hour,next_hour
            if hour == self._hour[0]:
                increment_day = True

        print 'Current:',self.current
        nexttime = nexttime.replace(second=second, minute=minute, hour=hour, microsecond=0)
        print "next call time:",nexttime
        waittime = nexttime - self.current
        print 'Wait',waittime.seconds
        return waittime.seconds

    def _is_int(self, s):
        try:
            int(s)
            return True
        except:
            return False

    def _is_valid_chars(self, s):
        """
        returns True if the string [s] contains only integers, and [*/,-]
        """
        return not len(self._invalidchars.findall(s))

    def _parse_cronstring(self, timeunit, cronstring):
        if self._seq.match(cronstring):
            return self._expand_sequence(cronstring)
        elif self._step.match(cronstring):
            return self._expand_step(timeunit, cronstring)

    def _expand_step(self, timeunit, cronstring):
        assert len(self._numbers.findall(cronstring)) == 1, \
            'Cannot have more than one step declaration in a cronstring: {0}'.format(cronstring)
        step = int(self._numbers.findall(cronstring)[0])
        maxstep = max(self.TIMEUNITS[timeunit])
        sequence = []
        for mult in range((maxstep / step)+1):
            sequence.append(mult * step)
        return sequence

    def _expand_sequence(self, cronstring):
        """
        Given the input for a type of timestep (e.g. minute, hour, etc), expands the crontab
        entry to the full set of timesteps indicated
        """
        sequence = []
        if isinstance(cronstring, int):
            sequence.append(cronstring)
            return sequence
        for chunk in cronstring.split(','):
            # test if integer/float. If it is, then add to our list
            if self._is_int(chunk):
                sequence.append(int(chunk))
            if '-' in chunk:
                try:
                    begin,end = map(int,chunk.split('-'))
                    # sequence 7-10 will yield [7,8,9,10]
                    sequence.extend(range(begin,end+1))
                except ValueError:
                    raise ValueError("Please ensure that ranges follow the form of 'x-y', where x,y are ints and x < y")
        # sort sequence in ascending order
        return sorted(sequence)

    def _check_range(self, timeunit, cronstring):
        valid_range = self.TIMEUNITS[timeunit]
        for digit in self._numbers.findall(cronstring):
            if not int(digit) in valid_range:
                raise ValueError("Range {0} is invalid for time unit {1}".format(cronstring, timeunit))


    def next_calltime(self):
        pass

class CronDecorator(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, *args):
        self.f(*args)



if __name__=='__main__':
    cs = CronSchedule(second='1,3,5-10')
