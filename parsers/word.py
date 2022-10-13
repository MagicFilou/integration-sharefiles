import docx2txt

from parsers import Parser

class WordParser(Parser):
    # This is a very limited parsing. We should extend with something
    # deeper.
    ACCEPTED_TYPES = ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".doc", ".docx"]

    def parse(self, item):
        super().parse(item)

        # We assume this is a filepath we can read from
        yield (
            docx2txt.process(item),
            "full"
            # {   
            #     "type": "word",
            #     "position":{}
            # }
        )


if __name__ == "__main__":
    import sys
    parser = WordParser(None) # Fake the source for now.
    for data in parser.parse(sys.argv[1]):
        text, meta = data
        print(data)

