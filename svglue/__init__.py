#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lxml import etree


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

            if elem.tag == '{http://www.w3.org/2000/svg}rect':
                self._rect_subs[tid] = (elem.get('width'), elem.get('height'),
                                        elem.get('x'), elem.get('y'))
                elem.getparent().remove(elem)
            elif elem.tag == '{http://www.w3.org/2000/svg}tspan':
                self._tspan_subs[tid] = elem
            else:
                raise TemplateParseError(
                    'Can only replace <rect> and <tspan> elements, found %s '
                    'instead' % (elem.tag,)
                )

    def set_text(self, tid, text):
        self._tspan_subs[tid].text = text

    def __str__(self):
        return etree.tostring(self._doc)


load = Template.load
from_string = Template.from_string
