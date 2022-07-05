import os

try:
    from .developer import *
except ImportError:
    from .production import *
