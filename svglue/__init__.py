#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree


RECT_TAG = '{http://www.w3.org/2000/svg}rect'
TSPAN_TAG = '{http://www.w3.org/2000/svg}tspan'
IMAGE_TAG = '{http://www.w3.org/2000/svg}image'
IMAGE_HREF = '{http://www.w3.org/1999/xlink}href'


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

    def set_text(self, tid, text):
        self._tspan_subs[tid].text = text

    def set_image(self, tid, href):
        elem = self._rect_subs[tid]
        elem.tag = IMAGE_TAG

        ALLOWED_ATTRS = ('x', 'y', 'width', 'height', 'style')
        for attr in elem.attrib.keys():
            if not attr in ALLOWED_ATTRS:
                del elem.attrib[attr]

        elem.set(IMAGE_HREF, href)
        elem.set('preserveAspectRatio', 'none')


    def __str__(self):
        return etree.tostring(self._doc)


load = Template.load
from_string = Template.from_string
