import os
import fitz
import shutil
import pdfoutline
import pytesseract
import PyPDF2
from fpdf import FPDF
from PIL import Image
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from bert import *


pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' # путь к утсановленному tesseract-ocr


def image_to_text(img):
    return pytesseract.image_to_string(Image.open(img), lang='rus')


def get_text_from_not_ocr_pdf(document): # самое длинное названии функции в истории
    trash = "trash"
    try:
        shutil.rmtree(trash)
        os.mkdir(trash)
    except FileNotFoundError:
        os.mkdir(trash)
    doc = fitz.open(document)
    pdf_reader = PyPDF2.PdfReader(document)
    for i in range(len(doc)):
        page = doc.load_page(i)  # number of page
        box = pdf_reader.pages[i]
        width = int(float(box.mediabox.width) * 0.3527)
        height = int(float(box.mediabox.height) * 0.3527)
        if width > height:
            page.set_rotation(90)
        pix = page.get_pixmap(dpi=200)
        output = f"{i+1}.png"
        pix.save(os.path.join(trash, output))
    doc.close()
    pics = sorted(os.listdir(trash), key=lambda x: int(x[:x.find(".")]))
    pics = [os.path.join(trash, pic) for pic in pics]
    with ProcessPoolExecutor(max_workers=os.cpu_count() // 2 - 1) as executor:
        tasks = {executor.submit(image_to_text, img_path): img_path for img_path in pics}
        for future in concurrent.futures.as_completed(tasks):
            page_number = tasks[future]
            data = future.result(), page_number[-5]
            yield data


def add_toc(document, toc, new_document_name):
    pdfoutline.pdfoutline(document, toc, new_document_name)


def make_hyperlinks_page(f, toc):
    pdf = FPDF()
    trash = "trash"
    pics = sorted(os.listdir(trash), key=lambda x: int(x[:x.find(".")]))
    pics = [os.path.join(trash, pic) for pic in pics]
    pdf_reader = PyPDF2.PdfReader(f)
    for i, pic in enumerate(pics):
        pdf.add_page()
        box = pdf_reader.pages[i]
        width = int(float(box.mediabox.width) * 0.3527)
        height = int(float(box.mediabox.height) * 0.3527)
        if width > height:
            width, height = height, width
        pdf.image(Image.open(pic), x=0, y=0, w=width, h=height)
    pdf.add_page()
    font_dir = '/usr/share/fonts/truetype/freefont'
    pdf.add_font("Serif", style="B", fname=f"{font_dir}/FreeSerif.ttf")
    pdf.set_font("Serif", "B", size=20)
    pdf.cell(w=pdf.epw, text="Содержание", align="C")
    pdf.set_font("Serif", "B", size=15)
    pdf.cell(0, 10, "", new_x="LMARGIN", new_y="NEXT")
    for el in toc:
        pdf.cell(0, 10, f"{el[0]} {el[1]}", new_x="LMARGIN", new_y="NEXT", link=pdf.add_link(page=el[1]))
    output = "output.pdf"
    pdf.output(output)


def make_table_of_contents(document):
    with fitz.open(document) as doc:
        if len(doc.get_toc()) != 0:
            print("TOC already exists")
            f = ""
            make_hyperlinks_page(f)
            exit(0)
    all_text = {}
    with fitz.open(document) as doc:
        for num, page in enumerate(doc.pages()):
            all_text[num] = page.get_text()

    err = 5
    lines_count = sum([len(all_text[page].split()) for page in all_text.keys()])
    if lines_count + err * 30 < len(all_text.keys()) * 30: # проверка количества заранее неоцифрованных строк (ешё надо подумать)
        text_per_page = get_text_from_not_ocr_pdf(document)
        text_per_page = sorted(text_per_page, key=lambda el: el[1])
        text_per_page = [el[0] for el in text_per_page]
    else:
        text_per_page = [all_text[page] for page in all_text.keys()]

    toc = []
    for i, text in enumerate(text_per_page):
        tmp = get_key_words(text)
        tmp = [(el, i + 1) for el in tmp]
        toc += tmp
    
    make_hyperlinks_page(document, toc)
    tmp = "output.pdf"
    
    with open("toc.toc", 'w') as f:
        for i in range(len(toc)):
            f.write(f"{toc[i][0]} {toc[i][1]}\n")

    add_toc(tmp, "toc.toc", "new.pdf")

    os.remove(tmp)

