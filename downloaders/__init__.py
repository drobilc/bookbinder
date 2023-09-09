from .exceptions import *
from .fanfiction import FanfictionDownloader
from .json import JSONDownloader
from .ao3 import ArchiveOfOurOwnDownloader

DOWNLOADERS = {
    'fanfiction': FanfictionDownloader,
    'json': JSONDownloader,
    'ao3': ArchiveOfOurOwnDownloader,
}