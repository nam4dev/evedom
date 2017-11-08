# -*- coding: utf-8 -*-
"""
Define a set of functions helping Endpoints auto loading.

Based on a path and an optional folder,
auto loads all Endpoint according a single criteria:

    * Endpoint inheritance check (ie. should be a sub Class of Endpoint)
"""
import os
import os.path as path

from fnmatch import filter
from importlib import util

from evedom.endpoint import Endpoint

__author__ = "nam4dev"
__created__ = '08/11/2017'

# 'Protected' Global Endpoint(s)
_endpoints = {}


def _filter_valid_py(files):
    """
    Filter the python file which does not start with a `_`

    Args:
        files (list): A list of basename

    Returns:
        list: The filtered basename(s)
    """
    return [f for f in filter(sorted(files), r'*.py') if not f.startswith('_')]


def _compute_depth(rt, root):
    """
    Extract the delta between Root top folder
    and the `os.walk` generator root folder if any
    Represent the sub folder(s) according to the Root top

    Args:
        rt (str): The `os.walk` generator root folder
        root (str): The Root top folder path

    Returns:
        str: The delta/depth if any
    """
    return [seg for seg in str(rt[len(root):]).split(os.sep) if seg]


def _compute_logical_module_data(rt, py_file, depth):
    """
    Compute logical module data (path, name)

    Args:
        rt (str): The `os.walk` generator root folder
        py_file (str): The python basename
        depth (str): The depth if any

    Returns:
        tuple[str, str]: The module path & name
    """
    return path.join(rt, py_file), '.'.join(depth + [py_file[:-3]])


def _compute_endpoints_candidates(folder, module_name, module_path):
    """
    Get all endpoint candidate(s)

    Args:
        folder (str): The given folder containing endpoint(s) if so
        module_name (str): The module name
        module_path (str): The module path

    Returns:
        list: Endpoint Candidate(s)
    """
    endpoints_candidates = []
    try:
        loaded_spec = util.find_spec(
            '{}.{}'.format(folder, module_name) if folder else module_name,
            module_path
        )
        if loaded_spec:
            loaded_module = loaded_spec.loader.load_module()
            endpoints_candidates = [
                getattr(loaded_module, m, None) for m in dir(loaded_module)
                if not m.startswith('_') and m != 'Endpoint'  # base class
            ]
    except ImportError:
        pass
    return [candidate for candidate in endpoints_candidates if candidate]


def _handle_candidate(candidate):
    """
    Validate/Set the Candidate
    into the global `endpoints` map
    if it is an valid Endpoint sub Class

    Args:
        candidate: Any kind of object
    """
    global _endpoints

    try:
        if not issubclass(candidate, Endpoint):
            raise TypeError

        if candidate.name not in _endpoints:
            _endpoints[candidate.name] = candidate

    except (TypeError, RuntimeError):
        pass


def _auto_load_endpoints(root=None, folder=None, excluded=None):
    """
    Auto load all Endpoint(s) found in given path

    Args:
        root (str): Root folder absolute path
        folder (str): Optional folder name
        excluded (list|tuple): Excluded file name pattern(s)
    """
    excluded = excluded or []
    root = path.join(root, folder) if folder else root

    for rt, _, files in os.walk(root):
        depth = _compute_depth(rt, root)

        for py_file in _filter_valid_py(files):
            m_path, name = _compute_logical_module_data(rt, py_file, depth)
            if name in excluded:
                continue

            candidates = _compute_endpoints_candidates(
                folder, name, m_path
            )

            for candidate in candidates:
                _handle_candidate(candidate)

    print('Found endpoints', _endpoints)


def init():
    """
    Initialize all Endpoint(s) found

    It shall be called with a Flask Application Context,
    otherwise, it will fail

    Raises:
        RuntimeError: If called outside of an Application Context
    """
    for endpoint in _endpoints.values():
        endpoint()


def domain(root=None, folder=None, excluded=None):
    """
    Load endpoint(s) into a Domain map

    Args:
        root (str): Root folder absolute path as a String
        folder (str): Optional folder name as a String
        excluded (list|tuple): Excluded file name pattern(s)

    Returns:
        dict: The Domain map
    """
    # load only once
    if not _endpoints:
        _auto_load_endpoints(root=root, folder=folder, excluded=excluded)
    return {k: v.spec for k, v in _endpoints.items() if not v.wrapper}
