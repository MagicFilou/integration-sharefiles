from utils.constants import HANDLER, PATH

class Parser():
    """Abstract parser to inherit from.

    """
    ACCEPTED_TYPES = []

    def __init__(self, source):
        self.source = source

    def parse(self, item):
        # Check type here.
        pass

    #this won't work because you need to have instanciated your class in order to access self
    def accept_mimetype(self, mimetype="unkown"):
        return mimetype in self.__class__.ACCEPTED_TYPES

from parsers.pcsv import CSVParser
from parsers.excel import ExcelParser
from parsers.powerpoint import PowerPointParser
# from parsers.pdf import PDFParser
from parsers.text import TextParser
from parsers.word import WordParser