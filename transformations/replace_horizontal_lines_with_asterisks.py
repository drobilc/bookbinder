from bs4 import BeautifulSoup

from transformations.transformation import Transformation

class ReplaceHorizontalLinesWithAsterisks(Transformation):

    ACTIVATION_COMMAND = '--replace-horizontal-lines-with-asterisks'
    COMMAND_DESTINATION = 'replace_horizontal_lines_with_asterisks'

    def apply(self, arguments, ebook):
        stars_element = BeautifulSoup('<p style="text-align: center; font-size: 2em;">* * *</p>', 'html5lib')
        for chapter in ebook.data:
            html = BeautifulSoup(chapter, 'html5lib')
            lines = html.find_all('hr')
            for line in lines:
                line.replace_with(stars_element)
            chapter = html