# Bookbinder

*Bookbinder* is a user-friendly Python script created to effortlessly fetch stories from popular online platforms like Fanfiction, Archive of Our Own, and Wattpad and transform them into portable ebooks for convenient offline reading.

## Installation

To install, make sure that you are using at least **Python 3.6**, as the script relies on f-strings.

```
# Clone the repository
git clone https://github.com/drobilc/bookbinder.git

cd bookbinder

# Install the project requirements
pip install -r requirements.txt
```

## Usage

Bookbinder currently supports the following sources:

* [FanFiction](https://www.fanfiction.net/)
* [Archive of Our Own](https://archiveofourown.org/)
* JSON - intermediate representation for further processing

It can generate the following outputs:

* [epub file format](https://en.wikipedia.org/wiki/EPUB)
* audiobook (experimental)
* JSON - intermediate representation for further processing

### Standard usage

To create an ebook, you need to specify both a source and an ebook generator. The source indicates where to fetch the story, while the ebook generator transforms the downloaded content into the desired output file format.

Below is an example of how to download a story with the `<STORY_ID>` from the FanFiction website and convert it into an epub file called `ebook.epub`, which is compatible with most ebook readers. You can also set the destination file using the `--output-file` flag. If this flag is not used, the script, `generate_ebook.py`, will create a file named `book.epub`.

```bash
# Download a story from FanFiction, convert it to epub file format and save it as ebook.epub
python3 generate_ebook.py fanfiction epub <STORY_ID> --output-file ebook.epub
```
To download a story from Archive of Our Own (AO3), you can use the following command. In this case, the generator will create an epub file named `book.epub` as the default output.

```bash
# Download a story from Archive of Our Own (AO3), convert it to epub file format and save it as book.epub (default value)
python3 generate_ebook.py ao3 epub <STORY_ID>
```

### JSON

At times, there may be a need to preserve a downloaded story in an intermediate format for potential future use in generating an output. In such cases, the JSON source and output option comes in handy. By designating it as the destination, the story will be fetched and preserved within a machine-readable JSON file. Later, when you intend to transform it into a finalized ebook, simply rerun the generator, specifying the JSON file as the input source. This way, you can conveniently generate ebooks from previously stored story data.

```bash
# Download a story from Archive of Our Own (AO3) and store it as JSON
python3 generate_ebook.py ao3 json <STORY_ID> --output-file story.json

# Read the downloaded JSON file and convert it into epub
python3 generate_ebook.py json epub story.json --output-file ebook.epub
```

### Sources

#### FanFiction source

The FanFiction URL follows this structure: `https://www.fanfiction.net/s/<STORY_ID>/<CHAPTER>/<STORY_SLUG>`. In order to download a story, you must provide the `<STORY_ID>` argument to the ebook generator script.

To download a story and create an ebook file named home_with_the_fairies.epub from the following URL `https://www.fanfiction.net/s/6024634/1/Home-with-the-Fairies``, use the following command:

```bash
python3 generate_ebook.py fanfiction epub 6024634 --output-file home_with_the_fairies.epub
```

##### Additional information

The FanFiction website employs Cloudflare protection to identify and prevent bot access attempts. To get around this, the [undetected-chromedriver](https://pypi.org/project/undetected-chromedriver/2.1.1/) library is used. For it to work, Google Chrome and the Python Selenium library must be installed on the system. When downloading a story, a new visible chrome window will appear and we will be able to monitor the scraper getting the story. To maintain a low profile and avoid detection by Cloudflare's bot-detection mechanisms, we introduce a deliberate delay, which does slow down the scraper significantly.

#### Archive of Our Own source

The AO3 (Archive of Our Own) URL has the following structure: `https://archiveofourown.org/works/<STORY_ID>`. To download a story, you need to provide the `<STORY_ID>` argument to the ebook generator script.

To download a work and generate an ebook file `ao3_304382.epub` from the following URL `https://archiveofourown.org/works/304382`, use the following command:

```bash
python3 generate_ebook.py ao3 epub 304382 --output-file ao3_304382.epub
```

### Destinations

#### Epub file format destination

#### Audiobook

Bookbinder is able to create an audiobook using the [TTS](https://pypi.org/project/TTS/) text-to-speech and [pydub](https://pypi.org/project/pydub/) audio manipulation libraries. It supports choosing a text-to-speech generation model using the `--tts-model` flag. The text-to-speech speaker can be changed using the `--tts-speaker` flag. More information about TTS models and speakers can be found in the [TTS library documentation](https://tts.readthedocs.io/en/latest/index.html).

| Flag | Default value |
| ---- | ------------- |
| `--tts-model` | `tts_models/en/vctk/vits` |
| `--tts-speaker` | `p238` |

To create an audiobook `audiobook.wav` from JSON file `ebook.json`, we can use the following command.

```bash
python3 generate_ebook.py json audiobook ebook.json --output-file audiobook.wav
```