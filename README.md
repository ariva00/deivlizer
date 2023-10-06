# DEIVLIZER

Deivlizer is a tool to extract single slides from multi-slide pdf pages.

## What you need to run it

You'll need the python3 enviroment with the following packages:

- numpy
- Pillow
- opencv
- pypdfium2

To install the packages simply run:

```bash

pip install -r requirements.txt

```

## How to use it

To use the tool you need to run the following command:

```bash

python3 deivlizer.py <filename> -o <output>

```

Note that the output argument is optional and the default is ```out.pdf```.

The other optional arguments are listed with the ```-h``` flag and are:

- ```--scale```: Resolution scale of render (scale * 72dpi = output resolution)
- ```--kernel```: Kernel size for the morphological opening operation
- ```--coord```: Reference coordinate for background color detection

## How it works

The tool uses [pypdfium2](https://github.com/pypdfium2-team/pypdfium2)
to render each page of the pdf into a bitmap image.

For each page the background color is sampled in at the coordinates specified
by the ```-coord``` argument. The default coordinates are ```(0, 0)```.

The background is segmented using a connected components algorithm
and the mask is then cleaned up using a morphological opening operation.

The mask is then used to extract the slide from the original image and
a new pdf is created and saved.
