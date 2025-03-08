import os
import re
from collections import defaultdict
import pymupdf


update_blocks = False
update_md_file = True


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
    cells = table_finder.cells
    print(f"table number: {len(table_finder.tables)}")
    print(f"cell number: {len(table_finder.cells)}")
    print(f"cell bbox: {table_finder.cells}")
    # cell_content = page.get_textbox(table_finder.cells[0])
    # print("cell content:\n", cell_content)

    # get blocks
    blocks = page.get_text("blocks", sort=True)
    if update_blocks:
        with open("./files/stl-blocks.py", "w", encoding="utf-8") as out:
            out.write(str(blocks))
            print("output blocks file finished")

    md = ""
    ordered_item_pattern = r"(\d{1,2}|[a-z])\."  # ordered item，eg：1./a.
    unordered_item_pattern = r"○|□|▪"  # unordered item

    level_pos = defaultdict(int)
    ordered_number = defaultdict(lambda: 1)
    cur_level = 0  # for a non-orfered and non-unordered box to indent

    padding = blocks[0][0]  # horizontal distance between text bound and page bound
    page_width = page.rect.width
    last_right = 0
    esp = 5.0

    print(f"page width: {page_width}")
    print(f"padding: {padding}")

    for i in range(2, len(blocks) - 1):
        block = blocks[i]
        x = int(block[0])
        text = block[4].strip()

        # handle code block
        is_code = False
        for cell_rect in [pymupdf.Rect(cell) for cell in cells]:
            if cell_rect.contains(pymupdf.Rect(block[0], block[1], block[2], block[3])):
                is_code = True
                # print("a code block is found. code:\n", text)

                md += "\t" * (cur_level + 1) + "```\n"
                li = text.split()
                for line in li:
                    md += "\t" * (cur_level + 1) + line + "\n"
                md += "\t" * (cur_level + 1) + "```\n"
                break
        if is_code:
            continue

        ordered_match = re.search(ordered_item_pattern, text)
        unordered_match = re.search(unordered_item_pattern, text)
        xs = list(level_pos.keys())

        if ordered_match or unordered_match:  # is an item
            flag = False
            for _x, level in level_pos.items():
                if abs(_x - x) <= esp:
                    cur_level = level
                    ordered_number[cur_level] = ordered_number[cur_level] + 1
                    x = _x
                    flag = True
                    break
            if not flag:
                if level_pos:
                    # cur_level = level_pos[sorted(level_pos)[-1]] + 1
                    cur_level = level_pos[xs[-1]] + 1
                level_pos[x] = cur_level

            md += "\t" * cur_level  # indent
            if ordered_match:
                text = text.split()[1]
                md += str(ordered_number[cur_level]) + ". " + text
            elif unordered_match:
                begin = unordered_match.span()[1]
                md += "- " + text[begin:]
            md += "\n"
        else:  # section title or plain text under item
            if (not xs) or (xs and x <= xs[0]):  # section title
                md += "##### " + text + "\n"
            elif (
                page_width - padding - last_right <= esp
            ):  # last text block is wrapped because of bound but not newlined manually
                md = md[:-1] + text + "\n"  # remove newline in last block
            else:
                md += "\t" * (cur_level + 1) + text + "\n"
        last_right = block[2]

    if update_md_file:
        with open(dest_file, "w", encoding="utf-8") as out:
            out.write(md)
            print(f"{pdf_file} -> {dest_file} finished")


if __name__ == "__main__":
    pdf_file = "./files/stl.pdf"
    pdf2md(pdf_file)
