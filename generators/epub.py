from bs4 import BeautifulSoup
from ebooklib import epub

from generators.generator import Generator

class EpubGenerator(Generator):

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-file",
            default='book.epub',
            dest="output_file",
            help='The path to output ebook.',
        )
    
    def generate(self, arguments, ebook):
        # Create new epub book
        book = epub.EpubBook()

        # Set the book metadata
        book.set_identifier(str(ebook.metadata.get('story_id', 0)))
        book.set_title(ebook.metadata.get('title', 'Unknown'))
        book.set_language(ebook.metadata.get('language', 'en'))

        # Add the book author(s?)
        book.add_author(ebook.metadata.get('author', 'Unknown'))

        chapters = []
        for i, part in enumerate(ebook.data):
            # Create a new chapter and name it Chapter i
            chapter = epub.EpubHtml(title=f'Chapter {i + 1}', file_name=f'chapter{i+1}.xhtml', lang='en')
            html = BeautifulSoup(part, 'html5lib')
            chapter.content = html.prettify()
            
            # Add the chapter to the book
            book.add_item(chapter)
            chapters.append(chapter)

        # After all the chapters have been added, add a table of contents
        book.toc = (tuple(chapters))

        # Add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Add the book spine with all the chapters
        book.spine = ['nav'] + chapters

        # Write the file to disk
        epub.write_epub(arguments.output_file, book, {})