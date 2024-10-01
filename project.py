import os
import fitz
import shutil
import pdfoutline
import pytesseract
from PIL import Image
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from bert import *
import time


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
    for i in range(len(doc)):
        page = doc.load_page(i)  # number of page
        pix = page.get_pixmap()
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


def make_hyperlinks_page(f):
    # https://docs-python.ru/packages/modul-fpdf2-python/vneshnie-vnutrennie-ssylki/
    pass


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
        text_per_page = sorted([el[0] for el in get_text_from_not_ocr_pdf(document)], key=lambda el: el[1])
    else:
        text_per_page = [all_text[page] for page in all_text.keys()]

    toc = []
    for i, text in enumerate(text_per_page):
        tmp = get_key_words(text)
        tmp = [(el, i) for el in tmp]
        toc += tmp
    
    with open("toc.toc", 'w') as f:
        for i in range(len(toc)):
            f.write(f"{toc[i][0]} {toc[i][1] + 1}\n")

    add_toc(document, "toc.toc", "p.pdf")


print("поехали")
start = time.time()
document = 'test_1.pdf'
make_table_of_contents(document)
print(time.time() - start)

