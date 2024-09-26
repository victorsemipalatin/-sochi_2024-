import os
import shutil
import fitz
from PIL import Image
import pytesseract
import pdfoutline
from tqdm import tqdm


def find_images(f):
    doc = fitz.open(f)
    os.makedirs(trash)

    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images()

        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            if pix.n - pix.alpha > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            pix.save(os.path.join(trash, "page_%s-image_%s.png" % (page_index, image_index)))
            pix = None


def add_toc(pdf, toc, new_pdf_name):
    pdfoutline.pdfoutline(pdf, toc, new_pdf_name)


pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' # путь к утсановленному tesseract-ocr

trash = "trash"
pdf_dir = "train"
text_dir = "texts"
for folder in tqdm(os.listdir(pdf_dir)):
    for f in os.listdir(os.path.join(pdf_dir, folder)):
        text = {}
        document = os.path.join(pdf_dir, folder, f)
        with fitz.open(document) as doc:
            for num, page in enumerate(doc.pages()):
                text[num] = page.get_text()

        s = ""
        for page in text.keys():
            s += text[page]
            s += "\n"
        if set(s) == set(['\n', ' ']) or set(s) == set('\n') or set(s) == set(' ') or set(s) == set():
            find_images(document)
            s = ""
            for image in sorted(os.listdir(trash)):
                full_path = os.path.join(trash, image)
                s += pytesseract.image_to_string(Image.open(full_path), lang='rus')
                s += "\n"
        with open(os.path.join(text_dir, f.replace(".pdf", ".txt")), "w") as l:
            l.write(s)
    try:
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), trash) # папка почему-то не удаляется в тесте с новатэком
        shutil.rmtree(path)
    except Exception as err:
        print(err)


add_toc("test.pdf", "sample.toc", "test_with_toc.pdf")