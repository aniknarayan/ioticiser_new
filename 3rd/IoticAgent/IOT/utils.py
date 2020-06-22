# Copyright (c) 2016 Iotic Labs Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://github.com/Iotic-Labs/py-IoticAgent/blob/master/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Utility functions
"""
from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

from uuid import UUID

from IoticAgent.Core.Const import R_FEED, R_CONTROL
from IoticAgent.Core.compat import ensure_unicode, raise_from, unicode_type, string_types, Iterable, re_compile

__FOC_STR_MAPPING = {'feed': R_FEED,
                     'control': R_CONTROL}
__FOC_CODE_MAPPING = {value: key for key, value in __FOC_STR_MAPPING.items()}
__PRIVATE_NAME_PATTERN = re_compile(r'^__.*[^_]_?$')


def hex_to_uuid(hstr):
    """Make a 32 ascii char hex into a 8-4-4-4-12 uuid
    """
    return unicode_type(UUID(ensure_unicode(hstr, name='hstr')))


def uuid_to_hex(uid):
    """Make 8-4-4-4-12 uuid into plain hex for the QAPI
    """
    return unicode_type(UUID(ensure_unicode(uid, name='uid')).hex)


def str_to_foc(sfoc):
    """Take a string of 'feed' or 'control' and return the QAPI Resource Const.R_FEED or R_CONTROL
    """
    try:
        return __FOC_STR_MAPPING[sfoc]
    except KeyError as ex:
        raise_from(ValueError('sfoc'), ex)


def foc_to_str(foc):
    """Take the QAPI Resource code and return string of 'feed' or 'control'
    """
    try:
        return __FOC_CODE_MAPPING[foc]
    except KeyError as ex:
        raise_from(ValueError('foc'), ex)


def version_string_to_tuple(version):
    return tuple(int(part) if part.isdigit() else part for part in version.split('.'))


def bool_from(obj, default=False):
    """
    Returns:
        True if obj is not None and its string representation is not 0 or False (case-insensitive). If obj is None,
        'default' is used.
    """
    return str(obj).lower() not in ('0', 'false') if obj is not None else bool(default)


def private_name_for(var_name, cls):
    """
    Returns:
        Mangled variable name (if applicable) for the given variable and class instance. See
        https://docs.python.org/3/tutorial/classes.html#private-variables
    """
    if not (isinstance(var_name, string_types) and var_name):
        raise TypeError('var_name must be non-empty string')
    if not (isinstance(cls, type) or isinstance(cls, string_types)):  # pylint: disable=consider-merging-isinstance
        raise TypeError('cls not a class or string')
    if __PRIVATE_NAME_PATTERN.match(var_name):
        class_name = cls.__name__ if isinstance(cls, type) else cls
        return '_%s%s' % (class_name.lstrip('_'), var_name)
    else:
        return var_name


def private_names_for(cls, names):
    """
    Returns:
        Iterable of private names using privateNameFor()"""
    if not isinstance(names, Iterable):
        raise TypeError('names must be an interable')
    return (private_name_for(item, cls) for item in names)
