import pypdfium2 as pdfium
import cv2
import numpy as np
from PIL import Image
import argparse

def deivlize(args):

    pdf = pdfium.PdfDocument(args.filename)

    new_pdf = pdfium.PdfDocument.new()

    scale = args.scale
    mask_size = args.kernel * scale
    ref = {
        'x' : args.coord[0],
        'y' : args.coord[1]
    }

    for i in range(len(pdf)):
        page = pdf[i]
        bitmap = page.render(scale = scale, rotation=0)
        img = bitmap.to_numpy()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mask = img == img[ref['x'], ref['y'], :]
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
            if sort[i] != labels[ref['x'], ref['y']]:
                mask = (labels==sort[i]).astype(np.uint8)
                box = cv2.boundingRect(mask)
                cropped = img[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]

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
        
    new_pdf.save(args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('filename')
    parser.add_argument('-o', '--output', default='out.pdf', help='Output filename')
    parser.add_argument('-s', '--scale', default=6, type=int, help='Resolution scale of render (scale * 72dpi = output resolution)')
    parser.add_argument('-m', '--kernel', default=10, type=int, help='Kernel size for the morphological opening operation (scale invariant)')
    parser.add_argument('-x', '--coord', default=[0, 0], type=int, nargs=2, help='Reference coordinate for background color detection')

    args = parser.parse_args()

    deivlize(args)