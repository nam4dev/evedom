#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Write here what the module does...

"""
from bson import ObjectId
from eve.io.base import BaseJSONEncoder

__author__ = "nam4dev"
__created__ = '08/11/2017'


class EnhancedJSONEncoder(BaseJSONEncoder):

    def default(self, o):
        """
        Implement this method in a subclass such that it returns a
        serializable object for ``o``, or calls the base implementation (to
        raise a ``TypeError``).

        For example, to support arbitrary iterators, you could implement
        default like this::

            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                return JSONEncoder.default(self, o)
        """
        if isinstance(o, ObjectId):
            return str(o)
        return super(EnhancedJSONEncoder, self).default(o)
