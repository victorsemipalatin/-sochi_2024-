import os
import time
import fitz
from PIL import Image
import pytesseract


def find_images(f):
    doc = fitz.open(f)
    os.system(f"mkdir {dir_name}")

    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images()

        for image_index, img in enumerate(image_list, start=1):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            if pix.n - pix.alpha > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            pix.save(os.path.join(dir_name, "page_%s-image_%s.png" % (page_index, image_index)))
            pix = None


pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

file_name = "test_images.pdf"
f = file_name
file_path = ""
dir_name = "pages"

text = {}
with fitz.open(f) as doc:
    for num, page in enumerate(doc.pages()):
        text[num] = page.get_text()

s = ""
for page in text.keys():
    s += text[page]
    s += " "
if set(s) == set(['\n', ' ']) or set(s) == set('\n') or set(s) == set(' ') or set(s) == set():
    start = time.time()
    find_images(file_name)
    text = " "
    for file in sorted(os.listdir(dir_name)):
        full_path = os.path.join(dir_name, file)
        text += pytesseract.image_to_string(Image.open(full_path), lang='rus')
        text += " "
    print(text.split())
    os.system(f"rm -r {dir_name}")
    print(time.time() - start)
else:
    print(s.split())

