from processing import get_video_specs
from templatetags.duration import duration

from django import forms
from django.forms.util import flatatt
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

import datetime

class ReadOnlyWidget(forms.Widget):
    """
    A generic read-only widget.
    """
    def render(self, name, value, attrs):
        final_attrs = self.build_attrs(attrs, name=name)
        if hasattr(self, 'initial'):
            value = self.initial
            return mark_safe("<p %s>%s</p>" % (flatatt(final_attrs), escape(value) or ''))

    def _has_changed(self, initial, data):
        return False

class DurationInput(ReadOnlyWidget):
    """
    A widget displaying duration values, specified in seconds, in HH:MM:SS.MMM format.
    """
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        elif not isinstance(value, datetime.timedelta):
            value = datetime.timedelta(seconds=float(value))
        value = duration(value, 'H:I:S.M')
        return super(DurationInput, self).render(name, value, attrs)

#--------------------------
# Admin site custom widgets
#--------------------------

class AdminVideoWidget(forms.FileInput):
    """
    A file widget for the admin site, which shows information about the current video.
    """
    def __init__(self, attrs={}):
        super(AdminVideoWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = ['<div style="margin-left: 106px">']
        if value and hasattr(value, 'url'):
            output.append('<b>%s</b> %s<br />' % (_('Currently:'), value))
            specs = get_video_specs(value.path)
            if specs:
                output.append('<b>size</b> %sx%s pixels<br />' % (specs['width'], specs['height']))
                output.append('<b>duration</b> %s seconds<br />' % specs['duration'])
                output.append('<b>bitrate</b> %s kb/s<br />' % specs['bitrate'])
                if specs['video']: output.append('<b>video stream</b> %s<br />' % specs['video'])
                if specs['audio']: output.append('<b>audio stream</b> %s<br />' % specs['audio'])
        output.append(_('Change:'))
        output.append(super(AdminVideoWidget, self).render(name, value, attrs))
        output.append('</div>')
        return mark_safe(u''.join(output))

