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
"""Helper object for getting and setting metadata for an Iotic Point programmatically
"""

from .ResourceMeta import ResourceMeta, IOTIC_NS


class PointMeta(ResourceMeta):
    """PointMeta class does nothing more than its base class: ResourceMeta
    """

    _labelPredicate = IOTIC_NS.pointLabel
    _commentPredicate = IOTIC_NS.pointComment
