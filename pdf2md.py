import os
import re
import pymupdf


class Rect(object):
    def __init__(self, _x1=0, _y1=0, _x2=0, _y2=0):
        self.x1 = _x1
        self.y1 = _y1
        self.x2 = _x2
        self.y2 = _y2

    def contains(self, rect):
        return (
            self.x1 <= rect.x1
            and self.y1 <= rect.y1
            and self.x2 >= rect.x2
            and self.y2 >= rect.y2
        )


def pdf2md(pdf_file):
    pdf = pymupdf.open(pdf_file)
    dir = os.path.dirname(pdf_file)
    name = os.path.splitext(os.path.basename(pdf_file))[0]
    ext = ".md"
    dest_file = dir + "/" + name + "-pymupdf" + ext

    print(f"page count: {pdf.page_count}")

    page = pdf[0]

    # get code table (can only get cells, but not tables)
    table_finder = page.find_tables(strategy="lines_strict")
    cells = table_finder.tables
    # print(f"table number: {len(table_finder.tables)}")
    # print(f"cell number: {len(table_finder.cells)}")
    # print(f"cell bbox: {table_finder.cells[0]}")
    # cell_content = page.get_textbox(table_finder.cells[0])
    # print("cell content:\n", cell_content)

    # get blocks
    blocks = page.get_text("blocks", sort=True)
    md = ""
    tab = ""
    ordered_item_pattern = r"(\d{1,2}|[a-z])\."
    unordered_item_pattern = r"○|□|▪"

    for i, block in blocks:
        if i == 0 or i == 1:
            continue
        # md+=tab
        text = block[4]
        item_symbol = ""
        ordered_match = re.search(ordered_item_pattern, text)
        unordered_match = re.search(unordered_item_pattern, text)
        if ordered_match or unordered_match:
            li = text.split()
            if ordered_match:
                item_symbol = ordered_match.group()
                md += item_symbol + " "
            elif unordered_match:
                md += "- " + li[0]
                if len(li) >= 2:
                    md += li[0]


if __name__ == "__main__":
    pdf_file = "./files/stl.pdf"
    pdf2md(pdf_file)
