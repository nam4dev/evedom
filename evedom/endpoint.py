#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A common set of function to handle Endpoints,
in a handy & most generic manner based on Eve event hooks framework.
"""
import json

from eve.methods import get
from flask import current_app

from evedom.helpers.encoders import EnhancedJSONEncoder

__author__ = "nam4dev"
__created__ = '08/11/2017'


class Endpoint(object):
    """
    Endpoint base

    Offer some common utilities &
    A placeholder to order properly each Model separately

    Any Subclass shall define:

        * A name.
        * A specification dictionary.
        * All Eve defined callback methods shall be returned by `_on_methods` method
        ** ie. [('on_pre_POST_{}'.format(self.name), self._check_duplicates), ]
    """
    name = None
    spec = None
    wrapper = False

    @classmethod
    def resources_by_name(cls, resource_name, from_db=True):
        """

        """
        if from_db:
            return cls._db_resources_by_name(resource_name)
        return cls._eve_resources_by_name(resource_name)

    @classmethod
    def _eve_resources_by_name(cls, resource_name):
        """
        Get Eve-layer for the given resource
        Taking advantage of all Eve logic (auth, pagination, ...)

        Args:
            resource_name (str): The Resource name

        Returns:
            list: Items for the given resource
        """
        response, _, _, _, _ = get(resource_name)
        return response.get('_items') or []

    @classmethod
    def _db_resources_by_name(cls, resource_name):
        """
        Get under-layer db driver for the given resource
        
        Args:
            resource_name (str): The Resource name

        Returns:
            The Resource db driver (pymongo)
        """
        return current_app.data.driver.db[resource_name]

    @property
    def app(self):
        """
        Shortcut to get the current App
        
        Returns:
            The current App
        """
        return current_app

    @property
    def data(self):
        """
        Shortcut to get the current App data
        
        Returns:
            The current App data
        """
        return self.app.data

    @property
    def resources(self):
        """
        Holding DB Resources reference

        Returns:
            Under layer Flask DB Driver instance for the specific endpoint
        """
        if not self._resources:
            self._resources = self._db_resources_by_name(self.name)
        return self._resources

    def __init__(self):
        """
        Constructor

        At initialization time, each `Endpoint`:

            * Validates its own integrity
            * Loads its `on` callbacks
        """
        self._resources = None
        self._validate()
        self._set_callbacks()
        self._register()

    def _register(self):
        """
        Allow to register any custom endpoint
        """

    def _on_methods(self):
        """
        Default method - Shall be overridden by sub-classes

        Based on Eve's event hooks framework,
        a set of callback can be intelligently assigned to
        specific events

        Returns:
            list: Callbacks mapped to Eve event hooks framework.
        """
        return []

    def _validate(self):
        """
        Validate the Endpoint class itself with really tiny check, such as:

            * Name shall be defined
            * Specification shall be defined

        Note:
            This is the minimum required for Eve to work properly
            
        Raises:
            EndpointError: If any error encountered
        """

        errors = []
        if not self.name:
            errors.append("Name shall be defined! Got -> {}".format(self.name))
        if not self.wrapper:
            if not self.spec:
                errors.append("Specification shall be defined! Got -> {}".format(self.spec))
            if errors:
                raise EndpointError(', '.join(errors))

    def _set_callbacks(self):
        """
        Set all callbacks defined by sub classes into the Current App (Flask)
        """
        for name, method in self._on_methods():
            setattr(self.app, name, method)

    @classmethod
    def dumps(cls, payload, **options):
        """
        Wraps JSON dumps method to add Custom JSONEncoder
        
        Args:
            payload (list|dict): The JSON-able payload
            **options: Any options `json.dumps` method takes

        Returns: 
            str: The serialized payload
        """
        return json.dumps(payload, cls=EnhancedJSONEncoder, **options)


class EndpointError(ValueError):
    """
    Endpoint Exception base Class
    """
