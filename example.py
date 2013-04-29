#!/usr/bin/env python
# -*- coding: utf-8 -*-

import svglue


# load the template from a file
tpl = svglue.load(file='sample-tpl.svg')

# replace some text
tpl.set_text('sample-text', u'This was replaced.')

# replace the pink box with 'hello.png'. if you do not specify the mimetype,
# the image will get linked instead of embedded
tpl.set_image('pink-box', file='hello.png', mimetype='image/png')

# svgs are merged into the svg document (i.e. always embedded)
tpl.set_svg('yellow-box', file='Ghostscript_Tiger.svg')

# to render the template, cast it to a string. this also allows passing it
# as a parameter to set_svg() of another template
src = str(tpl)

# write out the result as an SVG image and render it to pdf using cairosvg
open('output.svg', 'w').write(src)
from cairosvg.surface import PDFSurface
PDFSurface.convert(src, write_to=open('output.pdf', 'w'))
