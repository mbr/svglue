svglue
======

svglue is a small library that takes a template in form of a specially prepared
SVG document and fills in text and images to create an output SVG file. Style
information like opacity, size, and ordering is kept.

It's mainly intended to be used to set up a nice workflow creating templates
for PDF generation:

  1. Create your template in Inkscape, a placeholder text-element where you
     want to fill in text later, or a rectangle for filling in images.
  2. Add a custom attribute ``template-id`` to every ``<tspan>`` or ``<rect>``
     element that you want to replace. Each ``template-id`` must be a unique
     identifier.
  3. Using ``svglue``, you can programmatically replace every text or rect
     using its ``template-id`` with either a raster image, another SVG graphic
     or replacement text.
  4. Finally, use something like `rsvg <http://cairographics.org/pyrsvg/>`_,
     `CairoSVG <http://cairosvg.org/>`_ or another SVG-renderer to create a PDF
     document.


Example code:
-------------

Step 3::

    #!/usr/bin/env python

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
    import cairosvg
    with open('output.pdf', 'w') as out, open('output.svg', 'w') as svgout:
        svgout.write(src)
        cairosvg.svg2pdf(bytestring=src, write_to=out)

It's important to note that versions <= 0.5 of ``cairosvg`` have a bug that
renders the tiger scaled incorrectly. For now, you can use a different renderer
for better results until that bug is fixed.


Installation
------------
``svglue`` is `available via PyPI <https://pypi.python.org/pypi/svglue/>`_, so
a simple ``pip install svglue`` should suffice to install.


API reference
-------------

Note that the main target for this library is Python3. The later
versions of `cairosvg` do not compile on Python2 anymore for me.

If you need Python2 support, restrict the version of `svglue` to `<=0.2.1`.

svglue.load(src=None, file=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Loads a template, returning a ``Template``-object. The ``src``/``file`` load
pattern is used through the library - ``src`` is a string containing the
source of the SVG file, or ``file`` can either be a file-like object (with a
``read()`` method) or a filename for the source file. Only one of
``src``/``file`` may be specified.

Template.set_text(tid, text)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Replaces the text inside the element ``<tspan id="tid">`` (whose id is the
actual ``tid``) with the specified ``text``.

Template.set_image(tid, src=None, file=None, mimetype=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Replaces a rectangle whose id is ``tid`` (``<rect id="tid">``) with an
``<image>`` tag to link/embed the specified image. If ``mimetype`` is ``None``,
the image is linked (so ``file`` should be the path/URI of thte image).

If ``mimetype`` is given (should be either ``image/png`` or ``image/jpeg``),
the supplied image is stored inline in the resulting SVG document.

Template.set_svg(tid, src=None, file=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Conceptually similiar to ``Template.set_image()``, this replaces a rectangle
with an SVG-image. However, no linking is supported, the SVG is copied into the
resulting SVG-documents ``<defs>``-section and a ``<use>``-Element replaces
the rectangle.

Since ``Template.__str__()`` (see below) is used to render templates, this
allows nesting templates by simply passing them as the second argument to
``set_svg()``.

Template.__str__()
~~~~~~~~~~~~~~~~~~
Renders the template. Returns the template with all supplied info filled in.
