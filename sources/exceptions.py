class DownloaderException(Exception):
    pass

class StoryDoesNotExistException(DownloaderException):
    pass

class ChapterDoesNotExistException(DownloaderException):
    pass