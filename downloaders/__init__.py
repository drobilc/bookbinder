from .exceptions import *
from .fanfiction import FanfictionDownloader

DOWNLOADERS = {
    'fanfiction': FanfictionDownloader,
}