# -*- coding: utf-8 -*-
#
# Google App Engineでpytzを使うのはディスクの無駄遣いらしいので
# JSTの分だけ定義した。
#
# ほとんど、以下のコピペ
# https://docs.python.org/2/library/datetime.html#tzinfo-objects
#
#import pytz
#import datetime
#tz = pytz.timezone(app.config['TZ'])  # time zone
#dt = tz.fromutc(i.date).strftime('%Y-%m-%d %H:%M:%S %Z%z')

from datetime import tzinfo, timedelta, datetime

ZERO = timedelta(0)

# A UTC class.

class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

class JST(tzinfo):
    """Implementation of the Japanese JST timezone."""
    def utcoffset(self, dt):
        return timedelta(hours=+9)
    
    def dst(self, dt):
        return ZERO
    
    def tzname(self, dt):
        return "JST"
