import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from bs4 import BeautifulSoup
from sources.source import Source
from sources.ebook import Ebook, Chapter
import time
import logging

from sources.exceptions import *

class FanfictionSource(Source):
    
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
    
    def get_chapter(self, page):
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
        
        # Get the title of the current chapter
        chapter_selector = html.find('select', {'id': 'chap_select'})
        selected_chapter = chapter_selector.find('option', selected=True)
        chapter_title = selected_chapter.get_text().strip()
        
        return Chapter(
            title=chapter_title,
            html=story_container.prettify(),
        )
    
    def configure_scraper(self):
        # Cloudflare bypass from the following link. Might not work in the future.
        # https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/1388#issuecomment-1632083471
        logging.debug(f'Initializing Chromedriver to bypass Cloudflare protection')
        first_chapter_url = f'https://www.fanfiction.net/s/{self.story_id}/1'
        self.driver.execute_script(f'''window.open("{first_chapter_url}","_blank");''')
        time.sleep(10)
        self.driver.switch_to.window(window_name=self.driver.window_handles[0])
        self.driver.close()
        self.driver.switch_to.window(window_name=self.driver.window_handles[0])
        time.sleep(2)
        self.driver.get("https://google.com")
        time.sleep(2)
        logging.debug(f'Chromedriver initialization done')

    def download(self, arguments):
        self.story_id = arguments.story_id
        self.page_load_timeout = arguments.page_load_timeout
        self.wait_between_requests = arguments.wait_between_requests
        
        # Construct a new undetected chrome driver that we will use to surpass
        # Cloudfare DDOS protection.
        self.driver = uc.Chrome()
        self.configure_scraper()

        logging.info(f'Story download started')

        story_metadata = self.get_metadata()
        logging.info(f'Downloaded story meta data')

        chapters = []

        current_page = 1
        while True:

            try:
                chapters.append(self.get_chapter(current_page))
                logging.info(f'Downloaded chapter {current_page}')
                time.sleep(self.wait_between_requests)
            except ChapterDoesNotExistException:
                # We have reached the end of the book. Break the infinite loop and
                # convert downloaded chapters into an ebook.
                logging.info(f'No more chapters available')
                break

            current_page += 1
        
        logging.info(f'Story download ended')
        
        return Ebook(
            title=story_metadata['title'],
            id=story_metadata['id'],
            authors=[story_metadata['author']],
            description=story_metadata['description'],
            chapters=chapters,
        )