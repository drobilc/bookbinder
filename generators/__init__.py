from .epub import EpubGenerator
from .json import JSONGenerator

GENERATORS = {
    'epub': EpubGenerator,
    'json': JSONGenerator,
}