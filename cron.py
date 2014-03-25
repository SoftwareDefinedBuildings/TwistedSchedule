from twisted.internet import reactor, defer
from twisted.internet.task import LoopingCall, deferLater

class CronSchedule(object):

    SECOND_RANGE = range(0,60)
    MINUTE_RANGE = range(0,60)
    HOUR_RANGE = range(0,24)
    DAY_OF_WEEK_RANGE = range(0,7) #Sunday = 0, Monday = 1, ..., Saturday = 6

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
        self._second = second
        self._minute = minute
        self._hour = hour
        self._day_of_week = day_of_week
        if not (self._second or self._minute or self._hour or self._day_of_week):
            raise ValueError("CronSchedule must be instantiated with at least one timestep")

    def _generate_sequence(self, cronstring):
        for chunk in cronstring.split(','):

            print chunk



    def next_calltime(self):
        pass

class CronDecorator(object):
    def __init__(self, f):
        self.f = f

    def __call__(self, *args):
        self.f(*args)
