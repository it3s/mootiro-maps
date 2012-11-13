# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from string import letters, digits
from random import choice

def randstr(l=10):
    chars = letters + digits
    s = ''
    for i in range(l):
        s = s + choice(chars)
    return s
