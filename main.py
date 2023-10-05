import pypdfium2 as pdfium
import cv2
import numpy as np
from PIL import Image

pdf = pdfium.PdfDocument('test.pdf')

new_pdf = pdfium.PdfDocument.new()

ncol = 2
nrow = 3
scale = 6
mask_size = 10 * scale

for i in range(len(pdf)):
    page = pdf[i]
    bitmap = page.render(scale = scale, rotation=0)
    img = bitmap.to_numpy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mask = img == img[0,0,:]
    mask = mask[:,:,0]
    mask = mask.astype(np.uint8) * 255

    _, labels = cv2.connectedComponents(mask)
    mask = (labels==labels[0,0]).astype(np.uint8)*255
    mask = cv2.dilate(mask, np.ones((mask_size)), iterations=1)
    mask = cv2.erode(mask, np.ones((mask_size)), iterations=1)
    mask = 255 - mask
    retval, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)

    sort = np.lexsort((centroids[:,0], centroids[:,1]))

    for i in range(retval):
        if sort[i] != labels[0,0]:
            mask = (labels==sort[i]).astype(np.uint8)
            contours,_ = cv2.findContours(mask.copy(), 1, 1)
            box = cv2.minAreaRect(contours[0])
            box = np.uint(cv2.boxPoints(box))
            cropped = img[box[0,1]:box[2,1], box[0,0]:box[2,0]]

            try:
                image = pdfium.PdfImage.new(new_pdf)
                image.set_bitmap(pdfium.PdfBitmap.from_pil(Image.fromarray(cropped)))
                width, height = image.get_size()

                matrix = pdfium.PdfMatrix().scale(width, height)
                image.set_matrix(matrix)

                page = new_pdf.new_page(width, height)
                page.insert_obj(image)
                page.gen_content()
            except ValueError:
                pass
    
new_pdf.save("output.pdf")

