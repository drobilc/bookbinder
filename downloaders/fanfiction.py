import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
from downloaders.downloader import Downloader
from downloaders.ebook import Ebook

from downloaders.exceptions import *

class FanfictionDownloader(Downloader):
    
    def add_arguments(self, parser):
        parser.add_argument("story_id")

        parser.add_argument(
            "--page-load-timeout",
            type=int,
            default=120,
            dest="page_load_timeout",
            help='How much time the downloader should wait for fanfiction.net server to respond.',
        )
    
    def get_metadata(self):
        # Load the first page of the story.
        self.driver.get(f'https://www.fanfiction.net/s/{self.story_id}/1')

        # Wait until the element containing page metadata is loaded. If the page
        # is not loaded in [self.page_load_timeout] seconds, an exception will
        # be thrown.
        metadata_container = WebDriverWait(self.driver, timeout=self.page_load_timeout).until(
            expected_conditions.any_of(
                expected_conditions.presence_of_element_located((By.ID, "profile_top")),
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "gui_normal"))
            )
        )
        
        # Extract story metadata using beautiful soup.
        html = BeautifulSoup(self.driver.page_source, 'html5lib')
        
        metadata_container = html.find('div', {'id': 'profile_top'})
        if metadata_container is None:
            raise StoryDoesNotExistException

        return {
            "id": self.story_id,
            "title": metadata_container.find('b', {'class': 'xcontrast_txt'}).text.strip(),
            "author": metadata_container.find_all('a', {'class': 'xcontrast_txt'})[0].text.strip(),
            "description": metadata_container.find_all('div', {'class': 'xcontrast_txt'})[0].text.strip()
        }
    
    def get_page(self, page):
        self.driver.get(f'https://www.fanfiction.net/s/{self.story_id}/{page}/')
        _ = WebDriverWait(self.driver, timeout=self.page_load_timeout).until(
            expected_conditions.any_of(
                expected_conditions.presence_of_element_located((By.ID, "storytext")),
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "gui_normal"))
            )
        )
        
        html = BeautifulSoup(self.driver.page_source, 'html5lib')
        
        # Find the story container on facfiction.net. If it doesn't exist, we
        # have reached the end of the story. In this case, raise a
        # [ChapterDoesNotExistException].
        story_container = html.find('div', {'id': 'storytext'})
        if story_container is None:
            raise ChapterDoesNotExistException
        
        return str(story_container)
    
    def download(self, arguments):
        self.story_id = arguments.story_id
        self.page_load_timeout = arguments.page_load_timeout
        
        # Construct a new undetected chrome driver that we will use to surpass
        # Cloudfare DDOS protection.
        self.driver = uc.Chrome()

        story_metadata = self.get_metadata()

        parts = []

        current_page = 1
        while True:

            try:
                html = self.get_page(current_page)
                parts.append(html)
            except ChapterDoesNotExistException:
                # We have reached the end of the book. Break the infinite loop and
                # convert downloaded chapters into an ebook.
                break

            current_page += 1
        
        return Ebook(
            metadata=story_metadata,
            data=parts,
        )