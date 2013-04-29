#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import uuid4

from lxml import etree


SVG_NS = 'http://www.w3.org/2000/svg'
RECT_TAG = '{http://www.w3.org/2000/svg}rect'
TSPAN_TAG = '{http://www.w3.org/2000/svg}tspan'
IMAGE_TAG = '{http://www.w3.org/2000/svg}image'
USE_TAG = '{http://www.w3.org/2000/svg}use'
HREF_ATTR = '{http://www.w3.org/1999/xlink}href'


class TemplateParseError(Exception):
    pass


class Template(object):
    @classmethod
    def from_string(self, s):
        return cls(etree.fromstring(s))

    @classmethod
    def load(cls, fn):
        return cls(etree.parse(fn))

    def __init__(self, doc):
        self._doc = doc
        self._rect_subs = {}
        self._tspan_subs = {}
        self._defs = None

        for elem in self._doc.xpath('//*'):
            tid = elem.get('template-id', None)
            if not tid:
                continue

            # FIXME: use own namespace?
            del elem.attrib['template-id']

            if elem.tag == RECT_TAG:
                self._rect_subs[tid] = elem
            elif elem.tag == TSPAN_TAG:
                self._tspan_subs[tid] = elem
            else:
                raise TemplateParseError(
                    'Can only replace <rect> and <tspan> elements, found %s '
                    'instead' % (elem.tag,)
                )

        defs = self._doc.xpath('/svg:svg/svg:defs', namespaces={'svg': SVG_NS})

        if defs:
            self._defs = defs[0]
        else:
            self._defs = self._doc.getroot().insert(
                0, etree.Element('{%s}defs' % SVG_NS)
            )

    def set_text(self, tid, text):
        self._tspan_subs[tid].text = text

    def set_image(self, tid, href):
        elem = self._rect_subs[tid]
        elem.tag = IMAGE_TAG

        ALLOWED_ATTRS = ('x', 'y', 'width', 'height', 'style')
        for attr in elem.attrib.keys():
            if not attr in ALLOWED_ATTRS:
                del elem.attrib[attr]

        elem.set(HREF_ATTR, href)
        elem.set('preserveAspectRatio', 'none')

    def set_svg(self, tid, src=None, file=None):
        if not (src == None) ^ (file == None):
            raise RuntimeError('Must specify exactly one of src or '
                               'file argument')

        if src:
            doc = etree.fromstring(src)
        else:
            doc = etree.parse(file)

        doc_id = str(uuid4())
        doc.getroot().set('id', doc_id)
        self._defs.append(doc.getroot())

        elem = self._rect_subs[tid]
        elem.tag = USE_TAG

        ALLOWED_ATTRS = ('x', 'y', 'width', 'height', 'style')
        for attr in elem.attrib.keys():
            if not attr in ALLOWED_ATTRS:
                del elem.attrib[attr]

        elem.set(HREF_ATTR, '#' + doc_id)

    def __str__(self):
        return etree.tostring(self._doc)


load = Template.load
from_string = Template.from_string
