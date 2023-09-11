from sources.source import Source
from sources.ebook import Ebook, Chapter
import json

from sources.exceptions import *

class JSONSource(Source):
    
    def add_arguments(self, parser):
        parser.add_argument(
            "input_file",
            default='book.json',
            help='The path to input json file.',
        )
    
    def parse_chapter(self, chapter_data):
        return Chapter(
            title=chapter_data.get('title', None),
            html=chapter_data.get('html', ''),
        )

    def parse(self, json_data):
        return Ebook(
            title=json_data.get('title', None),
            id=json_data.get('id', None),
            language=json_data.get('language', None),
            authors=json_data.get('authors', []),
            description=json_data.get('description', None),
            chapters=[self.parse_chapter(chapter) for chapter in json_data.get('chapters', [])],
        )

    def download(self, arguments):
        with open(arguments.input_file, 'r') as input_file:
            json_data = json.load(input_file)
            return self.parse(json_data)