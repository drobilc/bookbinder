import requests
from bs4 import BeautifulSoup
from downloaders.downloader import Downloader
from downloaders.ebook import Ebook, Chapter
import logging

from downloaders.exceptions import *

class ArchiveOfOurOwnDownloader(Downloader):
    
    def add_arguments(self, parser):
        parser.add_argument("story_id")
    
    def parse_chapter(self, chapter_container):
        # print(chapter_container.prettify())
        landmark = chapter_container.find('h3', {'id': 'work'})
        chapter_text = landmark.parent

        # Remove the landmark from chapter since it doesn't contain anything
        # useful.
        landmark.extract()

        title_container = chapter_container.find('h3', {'class': 'title'})
        
        return Chapter(
            title=title_container.get_text().strip(),
            html=chapter_text.prettify(),
        )
    
    def extract_metadata(self, html):
        metadata_container = html.find('div', {'id': 'workskin'})

        language = html.select_one('dd.language').get('lang')
        title = metadata_container.select_one('div.preface h2.title')
        summary = metadata_container.select_one('.summary .userstuff')
        author = metadata_container.select_one('a[rel="author"]')

        return {
            "id": self.story_id,
            "language": language,
            "title": title.get_text().strip(),
            "author": author.get_text().strip(),
            "description": summary.get_text().strip()
        }

    def extract_chapters(self, html):
        chapter_container = html.find('div', {'id': 'chapters'})
        chapter_elements = chapter_container.find_all('div', {'class': 'chapter'}, recursive=False)
        
        logging.info(f'Found {len(chapter_elements)} chapters')
        
        chapters = []
        for chapter in chapter_elements:
            chapters.append(self.parse_chapter(chapter))

        return chapters
        
    def download(self, arguments):
        self.story_id = arguments.story_id

        # Construct a new requests session that will retain all cookies and set
        # the default header with user agent that will be sent with EVERY
        # request.
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        })

        response = self.session.get(f'https://archiveofourown.org/works/{arguments.story_id}?view_adult=true&view_full_work=true')
        html = BeautifulSoup(response.text, 'html.parser')

        metadata = self.extract_metadata(html)
        chapters = self.extract_chapters(html)

        return Ebook(
            title=metadata['title'],
            id=metadata['id'],
            authors=[metadata['author']],
            description=metadata['description'],
            language=metadata['language'],
            chapters=chapters,
        )