import logging
import json
from generators.generator import Generator

class JSONGenerator(Generator):

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-file",
            default='book.json',
            dest="output_file",
            help='The path to output json.',
        )

    def generate_chapter(self, chapter):
        return {
            'title': chapter.title,
            'html': chapter.html,
        }
    
    def generate_book(self, book):
        return {
            'title': book.title if hasattr(book, 'title') else None,
            'id': book.id if hasattr(book, 'id') else None,
            'language': book.language if hasattr(book, 'language') else None,
            'authors': book.authors if hasattr(book, 'authors') else None,
            'description': book.description if hasattr(book, 'description') else None,
            'chapters': [self.generate_chapter(chapter) for chapter in book.chapters],

        }
    
    def generate(self, arguments, ebook):
        logging.info(f'JSON generation started')
        result = self.generate_book(ebook)
        
        with open(arguments.output_file, 'w+') as output_file:
            json.dump(result, output_file)
            logging.info(f'Written JSON data to {arguments.output_file}')

        logging.info(f'JSON generation ended')
        return result