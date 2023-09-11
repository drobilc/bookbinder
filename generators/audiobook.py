from bs4 import BeautifulSoup
import logging
from TTS.api import TTS
import tempfile
from pathlib import Path
from pydub import AudioSegment
from sources.ebook import Ebook

from generators.generator import Generator

class AudiobookGenerator(Generator):

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-file",
            default='ebook.wav',
            dest="output_file",
            help='The path to output audio file.',
        )

        parser.add_argument(
            '--tts-model',
            default='tts_models/en/vctk/vits',
            dest="tts_model",
            help='Which text-to-speech model to use to generate audiobook.',
        )

        parser.add_argument(
            '--tts-speaker',
            default='p238',
            dest="tts_speaker",
            help='Which text-to-speech speaker to use to generate audiobook.',
        )
    
    def generate_chapter(self, arguments, text, output_file):
        tts = TTS(arguments.tts_model)
        tts.tts_to_file(text, speaker=arguments.tts_speaker, file_path=output_file)

    def generate(self, arguments, ebook: Ebook):
        logging.info(f'Audiobook generation started')

        with tempfile.TemporaryDirectory() as temporary_directory:

            chapter_directory = Path(temporary_directory)

            logging.info(f'Temporary directory: {chapter_directory}')
            
            chapter_files = []
            for i, chapter in enumerate(ebook.chapters):

                # Extract all text from the downloaded website.
                html = BeautifulSoup(chapter.html, 'html5lib')               
                text = html.get_text(separator=" ", strip=True)

                # Create a new WAV file for each chapter.
                chapter_output_file = chapter_directory / f'chapter_{i}.wav'

                logging.info(f'Writing chapter audio to {chapter_output_file}')
                self.generate_chapter(arguments, text, chapter_output_file)

                chapter_files.append(chapter_output_file)
        
            # Merge the files into a single wav file
            segments = [AudioSegment.from_wav(f) for f in chapter_files]
            if len(segments) < 1:
                return None

            combined = segments[0]
            segments.pop()
            while len(segments) > 0:
                current = segments.pop(0)
                combined = combined + current
            
            combined.export(arguments.output_file, format="wav")

        logging.info(f'Audiobook generation ended')
        logging.info(f'Output file path: {arguments.output_file}')