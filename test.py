import pdfplumber
from fpdf import FPDF

def create_toc_pdf(toc, original_pdf, output_pdf):
    # Создание нового PDF с оглавлением
    pdf = FPDF()

    # Чтение оригинального PDF и добавление страниц
    with pdfplumber.open(original_pdf) as pdf_reader:
        for i, page in enumerate(pdf_reader.pages):
            pdf.add_page()
            pdf.image(page.to_image(), x=0, y=0, w=210, h=297)
    pdf.add_page()
    font_dir = '/usr/share/fonts/truetype/freefont'
    pdf.add_font("Serif", style="B", fname=f"{font_dir}/FreeSerif.ttf")
    pdf.set_font("Serif", "B", size=20)

    for el in toc:
        pdf.cell(0, 10, f"{el[0]} {el[1]}", new_x="LMARGIN", new_y="NEXT", link=pdf.add_link(page=el[1]))

    pdf.output(output_pdf)

# Пример использования
toc = [("включении список голосования", 1), ("Общества решение", 1),
      ("Общества включении вопроса повестку акционеров", 1),
("Общества список каидилатур голосовапия соответствующий", 1),
("основании решения акции", 2),
("Устав", 2),
("Акционерного", 2),
("ОГРН собрание устава, собрания акционеров очетешное", 2),
("собрания форму текст", 3),
("Голосование акционеров голосовашия", 3),
("Голосование повестки собрания акцио", 3),
("база", 4),
("Протокол собрания акционеров", 4),
("Секроарь собрания акциоверов опус устава подпунктом содержания:", 4),
("« 7. приобретение акций", 4),
("печатью", 5),
("Директор", 5),
("требованию", 6),
("Общества акциоперов мини голосующих акций", 6),
("Общества,", 6),
("Решеие", 6),
("Общества собрания акционеров", 6),
("Общества решение отказе собрание акциоперов", 6)]
original_pdf = 'p.pdf'
output_pdf = 'output.pdf'

create_toc_pdf(toc, original_pdf, output_pdf)