#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from logging import Formatter, CRITICAL, ERROR, WARNING, INFO, DEBUG
from sys import platform, stdout

RESET_SEQ = "\x1b[0m"
COLOR_SEQ = "%s%%s" + RESET_SEQ

COLORS = {
    'DEBUG': COLOR_SEQ % "\x1b[36m",                   # light blue
    'INFO': COLOR_SEQ % "\x1b[1;1m",                   # bold white
    'WARNING': COLOR_SEQ % "\x1b[1;33m",               # bold yellow
    'ERROR': COLOR_SEQ % "\x1b[1;31m",                 # bold red
    'CRITICAL': COLOR_SEQ % ("\x1b[1;33m\x1b[1;41m"),  # bold yellow over red
}

LOG_LEVELS = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'WARNING': WARNING,
    'ERROR': ERROR,
    'CRITICAL': CRITICAL,
}


def getLogLevel(name):
    try:
        return LOG_LEVELS[name.upper()]
    except KeyError:
        raise ValueError('Invalid log level: %s' % name)


class ColoredFormatter(Formatter):
    """
    Class written by airmind:
    http://stackoverflow.com/questions/384076/
    """
    def format(self, record):
        levelname = record.levelname
        msg = Formatter.format(self, record)
        if levelname in COLORS:
            if stdout.isatty():
                msg = COLORS[levelname] % msg
        else:
            print ("*" * 100, levelname, "(%s)" % type(levelname), "not in",
                    COLORS.keys())
        return msg


def createColoredFormatter(stream, fmt, datefmt):
    if (platform != 'win32'):
        return ColoredFormatter(fmt=fmt, datefmt=datefmt)
    else:
        return Formatter('%(message)s')
