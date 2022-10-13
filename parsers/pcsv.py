import csv
from parsers import Parser

class CSVParser(Parser):

    ACCEPTED_TYPES = ["text/csv", ".csv"]

    def parse(self, item):
        super().parse(item)
        
        file_handle = open(item,'r')
        # We assume this is a open file handle we can read from
        reader = csv.reader(file_handle)
        row_no = 0
        try:
            for row in reader:
                col_no = 0
                for value in row:

                    yield (
                        value,
                        self.get_meta(row_no, col_no)
                    )
                    col_no += 1
                row_no += 1
        except Exception as e:
            print('Error in the PCSV parser woith error', e)


    @staticmethod
    def get_meta(row, column):
        return f"{row},{column}"
        # return {
        #     "type": "csv_cell",
        #     "position":{
        #         "row": row,
        #         "col": column
        #     }
        # }


if __name__ == "__main__":
    import sys, json
    parser = CSVParser(None) # Fake the source for now.
    for data in parser.parse(open(sys.argv[1], "r")):
        text, meta = data
        print(data)
