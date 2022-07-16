from .exceptions import *
from .fanfiction import FanfictionDownloader
from .wattpad import WattpadDownloader

DOWNLOADERS = {
    'fanfiction': FanfictionDownloader,
    'wattpad': WattpadDownloader,
}