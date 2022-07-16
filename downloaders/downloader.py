class Downloader(object):
    
    def add_arguments(self, parser):
        """
            Add additional command line arguments to Python's `ArgumentParser`.

            If the parser needs additional user input, the arguments can be
            added here.
        """
        pass

    def download(self, arguments):
        """
            Download ebook information from input source.

            The arguments is a `Namespace` object containing parsed arguments
            from add_arguments method.

            Returns an `Ebook` object containing the book metadata and list of
            chapters.
        """
        pass