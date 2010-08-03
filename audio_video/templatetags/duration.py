from django import template
from django.utils.dateformat import Formatter

register = template.Library()

class DurationFormat(Formatter):
    def __init__(self, d):
        self.data = d

    def h(self):
        "Hours, no leading zero; i.e. '0', '1', '10' , '20'..."
        return int(self.data.seconds / 3600)

    def H(self):
        "Hours with leading zero; i.e. '00', '01', '10'..."
        return u'%02d' % self.h()

    def i(self):
        "Minutes, no leading zero; i.e. '0' to '59'"
        return int(self.data.seconds / 60) - self.h() * 60

    def I(self):
        "Minutes with leading zero; i.e. '00' to '59'"
        return u'%02d' % self.i()

    def s(self):
        "Seconds; no leading zero; i.e. '0' to '59'"
        return self.data.seconds - self.h() * 3600 - self.i() * 60

    def S(self):
        "Seconds with leading zero; i.e. '00' to '59'"
        return u'%02d' % self.s()

    def m(self):
        "Milliseconds, variable precision; i.e. '0' to '999'"
        return self.data.microseconds * 1000

    def M(self):
        "Milliseconds, 3-digit fixed precision; i.e. '000' to '999'"
        return u'%03d' % self.m()

    def d(self):
        """
        Duration, in hours, minutes and seconds, with hours left off if they're
        zero, and without a leading zero on the left-most value.
        Examples: '5:30', '1:05:30', '11:15:30'
        """
        f = self.h() and 'h:I:S' or 'i:S'
        return self.format(f)

    def D(self):
        """
        Duration, in hours, minutes and seconds, with leading zeros.
        Examples: '00:05:30', '01:05:30', '11:15:30'
        """
        f = self.h() and 'H:I:S' or 'I:S'
        return self.format(f)

    def F(self):
        "Full timestamp: HH:MM:SS.MMM"
        return self.format('H:I:S.M')

@register.filter
def duration(value, arg):
    """Formats a duration (timedelta) according to the given format.
    """
    if value in (None, u''):
        return u''
    try:
        df = DurationFormat(value)
        return df.format(arg)
    except AttributeError, e:
        return e
duration.is_safe = False
