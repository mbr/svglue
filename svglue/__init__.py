#!/usr/bin/env python
# -*- coding: utf-8 -*-

from base64 import b64encode
from uuid import uuid4

from lxml import etree

SVG_NS = 'http://www.w3.org/2000/svg'
RECT_TAG = '{http://www.w3.org/2000/svg}rect'
TSPAN_TAG = '{http://www.w3.org/2000/svg}tspan'
FLOWPARA_TAG = '{http://www.w3.org/2000/svg}flowPara'
IMAGE_TAG = '{http://www.w3.org/2000/svg}image'
USE_TAG = '{http://www.w3.org/2000/svg}use'
HREF_ATTR = '{http://www.w3.org/1999/xlink}href'


class TemplateParseError(Exception):
    pass


class Template(object):
    @classmethod
    def load(cls, src=None, file=None):
        if not (src == None) ^ (file == None):
            raise RuntimeError('Must specify exactly one of src or '
                               'file argument')

        if src:
            return cls(etree.fromstring(src))

        return cls(etree.parse(file))

    def __init__(self, doc):
        self._doc = doc
        self._rect_subs = {}
        self._tspan_subs = {}
        self._flowpara_subs = {}
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
            elif elem.tag == FLOWPARA_TAG:
                self._flowpara_subs[tid] = elem
            else:
                raise TemplateParseError(
                    'Can only replace <rect> and <tspan> elements, found %s '
                    'instead' % (elem.tag, ))

        defs = self._doc.xpath('/svg:svg/svg:defs', namespaces={'svg': SVG_NS})

        if defs:
            self._defs = defs[0]
        else:
            self._defs = self._doc.getroot().insert(
                0, etree.Element('{%s}defs' % SVG_NS))

    def set_text(self, tid, text):
        self._tspan_subs[tid].text = text

    def set_flowtext(self, tid, text):
        self._flowpara_subs[tid].text = text

    def set_image(self, tid, src=None, file=None, mimetype=None):
        if not (src == None) ^ (file == None):
            raise RuntimeError('Must specify exactly one of src or '
                               'file argument')

        if not mimetype and (not file or hasattr(file, 'read')):
            raise RuntimeError('Must specify mimetype when not linking ',
                               'an image')

        elem = self._rect_subs[tid]
        elem.tag = IMAGE_TAG

        ALLOWED_ATTRS = ('x', 'y', 'width', 'height', 'style')
        for attr in elem.attrib.keys():
            if not attr in ALLOWED_ATTRS:
                del elem.attrib[attr]

        elem.set('preserveAspectRatio', 'none')

        # embed?
        if not mimetype:
            elem.set(HREF_ATTR, file)
        else:
            if not src:
                if not hasattr(file, 'read'):
                    file = open(file, 'rb')
                src = file.read()

            encoded = b64encode(src).decode('ascii')
            elem.set(HREF_ATTR, 'data:%s;base64,%s' % (mimetype, encoded))

    def set_svg(self, tid, src=None, file=None):
        if not (src == None) ^ (file == None):
            raise RuntimeError('Must specify exactly one of src or '
                               'file argument')

        if src:
            doc = etree.fromstring(str(src))
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
        return etree.tostring(self._doc, encoding='utf8', method='xml')


load = Template.load
