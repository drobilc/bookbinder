class Ebook(object):
    
    def __init__(self, title=None, id=None, language='en', authors=[], description=None, chapters=[]):
        self.title = title
        self.id = id
        self.language = language
        self.authors = authors
        self.description = description
        self.chapters = chapters

class Chapter(object):

    def __init__(self, title, html):
        self.title = title
        self.html = html