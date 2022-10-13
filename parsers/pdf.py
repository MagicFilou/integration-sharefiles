import PyPDF2
import pdftotext

from parsers import Parser

class PDFParser(Parser):

    ACCEPTED_TYPES = ["application/pdf", ".pdf"]

    def parse(self, item):
        super().parse(item)

        # We assume this is a open filehandle we can read from
        file_handle = open(item,'r')
        reader = PyPDF2.PdfFileReader(file_handle)

        doc_info = reader.documentInfo
        yield (
            "\n".join([
                "{key}: {value}".format(key=key, value=doc_info[key])
                for key in doc_info.keys()]),
            {"type": "documentInfo"}
        )

        pdf = pdftotext.PDF(item)
        page_no = 1
        for page in pdf:
            yield (
                page,
                {
                    "type": "page",
                    "position":{
                        "page_no": page_no
                    }
                }
            )
            page_no += 1


if __name__ == "__main__":
    import sys, json
    parser = PDFParser(None) # Fake the source for now.
    for data in parser.parse(open(sys.argv[1], "rb")):
        text, meta = data
        print(data)

