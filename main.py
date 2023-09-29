import pypdf
import copy

from pypdf.generic import RectangleObject

pdf_reader = pypdf.PdfReader('test.pdf')
pdf_writer = pypdf.PdfWriter()

print(len(pdf_reader.pages))

ncol = 2
nrow = 3

for page in pdf_reader.pages:

    witdh = page.mediabox.upper_right[0] / 2
    heigth = page.mediabox.upper_right[1] / 3

    for i in range(nrow - 1, -1, -1):
        for j in range(0, ncol, 1):
            slide = copy.deepcopy(page)
            slide.mediabox = RectangleObject((j * witdh, i * heigth, (j + 1) * witdh, (i + 1) * heigth))
            print(j, " ", i)
            print(slide.mediabox)
            pdf_writer.add_page(slide)

pdf_writer.write('output.pdf')