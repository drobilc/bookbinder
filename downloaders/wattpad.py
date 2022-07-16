import requests
from bs4 import BeautifulSoup
from downloaders.downloader import Downloader
from downloaders.ebook import Ebook
import time
import logging

from downloaders.exceptions import *

class WattpadDownloader(Downloader):
    
    def add_arguments(self, parser):
        parser.add_argument("story_id")

        parser.add_argument(
            "--page-load-timeout",
            type=int,
            default=120,
            dest="page_load_timeout",
            help='How many seconds the downloader should wait for fanfiction.net server to respond.',
        )

        parser.add_argument(
            "--wait-between-requests",
            type=int,
            default=5,
            dest="wait_between_requests",
            help='How many seconds the downloader should wait before downloading the next chapter. If this value is set too low, the Cloudfare DDOS protection might display captcha.',
        )
    
    def extract_metadata(self, html):
        metadata_container = html.find('div', {'class': 'story-info'})

        if metadata_container is None:
            raise StoryDoesNotExistException

        return {
            "id": self.story_id,
            "title": metadata_container.find('h3', {'class': 'item-title'}).text.strip(),
            "author": html.find('div', {'class': 'author'}).find_all('a')[-1].text.strip(),
            "description": metadata_container.find('p', {'class': 'item-description'}).text.strip()
        }
    
    def extract_chapter_links(self, html):
        chapters_list = html.find('ul', {'class': 'table-of-contents'})
        chapter_links = chapters_list.find_all('a')
        return [link.get('href') for link in chapter_links]
    
    def get_metadata(self):
        # Load the first page of the story.
        response = self.session.get(f'https://www.wattpad.com/{self.story_id}')
        
        html = BeautifulSoup(response.text, 'html5lib')

        # Extract story metadata using beautiful soup.
        metadata = self.extract_metadata(html)

        # Since the wattpad uses non-consecutive links for chapters, we must
        # also extract a list of links from the downloaded page. The downloader
        # will then use the links to download chapters.
        chapter_links = self.extract_chapter_links(html)
        return metadata, chapter_links
    
    def get_page(self, link):
        response = self.session.get(f'https://www.wattpad.com{link}')
        
        html = BeautifulSoup(response.text, 'html5lib')
        
        # Find the story container on wattpad.com, if it does not exist, then
        # something is wrong. Throw a [ChapterDoesNotExistException], so that
        # the downloader is notified.
        story_container_outer = html.find('div', {'id': 'sticky-end'})
        story_container = story_container_outer.find('pre')
        if story_container is None:
            raise ChapterDoesNotExistException

        # Remove sticky navigation from story container.
        sticky_navigation = story_container.find('div', {'id': 'sticky-nav'})
        if sticky_navigation is not None:
            sticky_navigation.decompose()
        
        # Remove all comments from the story.
        comment_containers = story_container.find_all('span', {'class': 'comment-marker'})
        for comment_container in comment_containers:
            comment_container.decompose()
        
        return str(story_container)
    
    def download(self, arguments):
        self.story_id = arguments.story_id
        self.page_load_timeout = arguments.page_load_timeout
        self.wait_between_requests = arguments.wait_between_requests
        
        # Construct a new requests session that will retain all cookies and set
        # the default header with user agent that will be sent with EVERY
        # request. If this specific header is not present, the site will return
        # a 403 response.
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        })

        logging.info(f'Story download started')

        story_metadata, story_chapters = self.get_metadata()
        logging.info(f'Downloaded story meta data')

        parts = []
        for chapter_link in story_chapters:
            try:
                html = self.get_page(chapter_link)
                parts.append(html)
                logging.info(f'Downloaded chapter {chapter_link}')
                time.sleep(self.wait_between_requests)
            except Exception:
                logging.exception('Could not download chapter')
        
        logging.info(f'Story download ended')

        return Ebook(
            metadata=story_metadata,
            data=parts,
        )