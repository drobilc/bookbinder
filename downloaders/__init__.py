from .exceptions import *
from .fanfiction import FanfictionDownloader
from .wattpad import WattpadDownloader
from .json import JSONDownloader

DOWNLOADERS = {
    'fanfiction': FanfictionDownloader,
    'wattpad': WattpadDownloader,
    'json': JSONDownloader,
}