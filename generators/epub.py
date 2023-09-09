from bs4 import BeautifulSoup
from ebooklib import epub
import logging

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
        logging.info(f'Epub generation started')
        # Create new epub book
        book = epub.EpubBook()

        # Set the book metadata
        book.set_identifier(str(ebook.id))
        book.set_title(ebook.title)
        book.set_language(ebook.language)

        # Add the book author(s?)
        for author in ebook.authors:
            book.add_author(author)

        chapters = []
        for i, chapter_data in enumerate(ebook.chapters):
            # Create a new chapter
            chapter = epub.EpubHtml(
                title=chapter_data.title,
                file_name=f'chapter{i+1}.xhtml',
                lang=book.language,
            )
            chapter.content = chapter_data.html
            
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
        logging.info(f'Epub generation ended')
        logging.info(f'Output file path: {arguments.output_file}')