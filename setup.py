#!/usr/bin/env python

from distutils.core import setup
from common.__init__ import __version__

setup(
        name="Waldur_Chatbot",
        version=__version__,
        packages=['common']
)
