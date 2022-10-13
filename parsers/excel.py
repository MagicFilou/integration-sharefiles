import xlrd

# import sys
# import os

# try:
#     sys.path.index(os.getcwd())
# except ValueError:
#     sys.path.append(os.getcwd())

from parsers import Parser

class ExcelParser(Parser):

    ACCEPTED_TYPES = ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                    ".xls", ".xlsx"]

    def parse(self, item):
        super().parse(item)

        # Item is a path to file
        wb = xlrd.open_workbook(item)

        sheet_names = wb.sheet_names()

        for idx in range(len(sheet_names)):
            sheet = wb.sheet_by_index(idx)

            #sheet.cell_value(0, 0)
            for i in range(sheet.nrows):
                for j in range(sheet.ncols):
                    value = sheet.cell_value(i, j)
                    if value:
                        value = str(value).strip()
                        if value:
                            yield (
                                value,
                                f"{sheet_names[idx]}_{i},{j}"
                                # {
                                #     "type": "excel",
                                #     "position":{
                                #         "sheet_name": sheet_names[idx],
                                #         "cell": {
                                #             "row": i,
                                #             "column": j,
                                #         }
                                #     }
                                # }
                            )


if __name__ == "__main__":
    import sys
    parser = ExcelParser(None) # Fake the source for now.
    for data in parser.parse(sys.argv[1]):
        text, meta = data
        print(data)

