from .exceptions import *
from .fanfiction import FanfictionSource
from .json import JSONSource
from .ao3 import ArchiveOfOurOwnSource

SOURCES = {
    'fanfiction': FanfictionSource,
    'json': JSONSource,
    'ao3': ArchiveOfOurOwnSource,
}