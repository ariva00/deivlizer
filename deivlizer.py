import pypdfium2 as pdfium
import cv2
import numpy as np
from PIL import Image
import argparse
import glob
from tqdm import tqdm
import os

def deivlize(args):

    pdf = pdfium.PdfDocument(args.filename)

    new_pdf = pdfium.PdfDocument.new()

    scale = args.scale
    mask_size = args.kernel * scale
    ref = {
        'x' : args.coord[0],
        'y' : args.coord[1]
    }

    for i in tqdm(range(len(pdf)), leave=False):
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

    parser.add_argument('filename', help='Input filename or source folder if in batch mode (see -b option)')
    parser.add_argument('-o', '--output', default='out.pdf', help='Output filename')
    parser.add_argument('-s', '--scale', default=6, type=int, help='Resolution scale of render (scale * 72dpi = output resolution)')
    parser.add_argument('-m', '--kernel', default=10, type=int, help='Kernel size for the morphological opening operation (scale invariant)')
    parser.add_argument('-x', '--coord', default=[0, 0], type=int, nargs=2, help='Reference coordinate for background color detection')

    parser.add_argument('-b', '--batch', default=False, action='store_true', help='Batch mode: filename is a source folder and output is a destination folder')

    args = parser.parse_args()

    if args.batch:
        os.makedirs(args.output, exist_ok=True)
        in_dir = args.filename
        out_dir = args.output
        for filename in tqdm(glob.glob(os.path.join(in_dir, '**', '*.pdf'), recursive=True)):
            args.filename = filename
            args.output = filename.replace(in_dir, out_dir, 1)
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            deivlize(args)
    else:
        deivlize(args)