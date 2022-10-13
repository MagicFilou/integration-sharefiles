from parsers import CSVParser

class TextParser(CSVParser):

    #accepted type for mix of mime and extensions which are mutualy exclusive
    ACCEPTED_TYPES = ["text/plain", ".txt", ".url"]

    @staticmethod
    def get_meta(row, column):
        return row
        # return {
        #     "type": "text",
        #     "position":{
        #         "line": row
        #     }
        # }


if __name__ == "__main__":
    import sys
    parser = TextParser(None) # Fake the source for now.
    for data in parser.parse(open(sys.argv[1], "r")):
        text, meta = data
        print(data)
