from bs4 import BeautifulSoup
import logging
from TTS.api import TTS
from pathlib import Path
from pydub import AudioSegment
from common.ebook import Ebook

from generators.generator import Generator

class AudiobookGenerator(Generator):

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-directory",
            default='audiobook',
            dest="output_directory",
            help='The directory in which to save the generated audiobook.',
        )

        parser.add_argument(
            '--tts-model',
            default='tts_models/en/vctk/vits',
            dest="tts_model",
            help='Which text-to-speech model to use to generate audiobook.',
        )

        parser.add_argument(
            '--tts-speaker',
            dest="tts_speaker",
            help='Which text-to-speech speaker to use to generate audiobook.',
        )

        parser.add_argument(
            "--merge-to-file",
            dest="merge_to_file",
            help='If set, all the chapters will be combined into a single file at this path.',
        )
    
    def generate_chapter(self, arguments, text, output_file):
        tts = TTS(arguments.tts_model)
        if arguments.tts_speaker is not None:
            tts.tts_to_file(text, speaker=arguments.tts_speaker, file_path=output_file)
        else:
            tts.tts_to_file(text, file_path=output_file)

    def generate(self, arguments, ebook: Ebook):
        logging.info(f'Audiobook generation started')

        # Check if the output directory already exists
        output_directory = Path(arguments.output_directory)
        if output_directory.exists():
            # The directory (or file) already exists. Check if it is a
            # directory, otherwise exit.
            if not output_directory.is_dir():
                # The output path is a file and not a directory, exit.
                logging.fatal(f'The output destination "{output_directory}" is not a directory.')
                return
            logging.info(f'The output directory "{output_directory}" already exists.')
        else:
            logging.info(f'The output directory "{output_directory}" doesn\'t exist, creating.')
            # The directory does not exist yet, create it.
            output_directory.mkdir(parents=True, exist_ok=True)
            logging.info(f'Output directory "{output_directory}" created.')

        # Now we can assume that the [output_directory] exists.            
        chapter_files = []
        for i, chapter in enumerate(ebook.chapters):

            # Extract all text from the downloaded website.
            html = BeautifulSoup(chapter.html, 'html5lib')               
            text = html.get_text(separator=" ", strip=True)

            # Create a new WAV file for each chapter.
            chapter_output_file = output_directory / f'chapter_{i}.wav'

            logging.info(f'Writing chapter audio to {chapter_output_file}')
            self.generate_chapter(arguments, text, chapter_output_file)

            chapter_files.append(chapter_output_file)
        
        logging.info(f'Audio for all chapters successfully generated')
    
        if arguments.merge_to_file is not None:
            logging.info(f'Merging all chapters into a single audio file: {arguments.merge_to_file}')

            # Merge the files into a single wav file
            segments = [AudioSegment.from_wav(f) for f in chapter_files]
            if len(segments) < 1:
                return None

            combined = segments[0]
            segments.pop()
            while len(segments) > 0:
                current = segments.pop(0)
                combined = combined + current
            
            combined.export(arguments.merge_to_file, format="wav")

            logging.info(f'Generated output file: {arguments.merge_to_file}')

        logging.info(f'Audiobook generation ended')