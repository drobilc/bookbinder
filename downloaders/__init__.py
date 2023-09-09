from .exceptions import *
from .fanfiction import FanfictionDownloader
from .json import JSONDownloader

DOWNLOADERS = {
    'fanfiction': FanfictionDownloader,
    'json': JSONDownloader,
}