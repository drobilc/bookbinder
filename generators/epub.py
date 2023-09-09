from ebooklib import epub
from downloaders.ebook import Ebook, Chapter
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
    
    def generate_cover(self, ebook_data: Ebook):
        # TODO: Generate cover
        return None

    def generate_introduction_page(self, ebook_data: Ebook):
        introduction = epub.EpubHtml(
            title=ebook_data.title,
            file_name=f'introduction.xhtml',
            lang=ebook_data.language,
        )

        authors = ", ".join(ebook_data.authors)
        introduction.content = f"""
            <h1 style="text-align: center;">{ebook_data.title}</h1>
            <p style="text-align: center;">{authors}</p><br>
            <p>{ebook_data.description}</p><br><br>
        """
        
        # Add the chapter to the book
        return introduction
    
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

        table_of_contents = []

        # Generate cover
        cover_page = self.generate_cover(ebook)
        if cover_page:
            book.add_item(cover_page)
            table_of_contents.append(cover_page)

        # Add the introduction page
        introduction_page = self.generate_introduction_page(ebook)
        book.add_item(introduction_page)
        table_of_contents.append(introduction_page)
        table_of_contents.append('nav')

        # Add all the book chapters
        for i, chapter_data in enumerate(ebook.chapters):
            chapter = epub.EpubHtml(
                title=chapter_data.title,
                file_name=f'chapter{i+1}.xhtml',
                lang=book.language,
            )
            full_content = f'<h2>{chapter_data.title}</h2>{chapter_data.html}'
            chapter.content = full_content
            
            # Add the chapter to the book
            book.add_item(chapter)
            table_of_contents.append(chapter)

        # After all the chapters have been added, add a table of contents
        book.toc = (tuple(table_of_contents))

        # Add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Add the book spine with all the chapters
        book.spine = table_of_contents

        # Write the file to disk
        epub.write_epub(arguments.output_file, book, {})
        logging.info(f'Epub generation ended')
        logging.info(f'Output file path: {arguments.output_file}')