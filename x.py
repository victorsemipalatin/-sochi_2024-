import pdfplumber 


with pdfplumber.open("test.pdf") as pdf:
  text = pdf.pages[0]
  clean_text = text.filter(lambda obj: obj['object_type'] == "char" and "Bold" in obj['fontname'])
  print(clean_text.extract_text())