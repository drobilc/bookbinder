from .epub import EpubGenerator
from .audiobook import AudiobookGenerator
from .json import JSONGenerator

GENERATORS = {
    'epub': EpubGenerator,
    'audiobook': AudiobookGenerator,
    'json': JSONGenerator,
}