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

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

from IoticAgent.Core.Validation import Validation
from IoticAgent.Core.utils import validate_nonnegative_int
from IoticAgent.Core.compat import Queue, Empty, monotonic

from .Point import PointDataObject
from .Exceptions import IOTSyncTimeout


class RemotePoint(object):
    """
    Base class for remote point types
    """

    def __init__(self, client, subid, pointid, lid):
        self.__client = client
        self.__subid = Validation.guid_check_convert(subid)
        self.__pointid = Validation.guid_check_convert(pointid)
        self.__lid = Validation.lid_check_convert(lid)

    @property
    def _client(self):
        """
        For internal use: reference to IOT.Client instance
        """
        return self.__client

    @property
    def subid(self):
        """
        **Advanced users only**
        The global subscription ID for the connection to this remote point in hex form (undashed).
        """
        return self.__subid

    @property
    def guid(self):
        """
        The Globally Unique ID of the Point you've followed (or attached to) in hex form (undashed).
        """
        return self.__pointid

    @property
    def lid(self):
        """
        Local id of thing which is following to this feed / attached to this control
        """
        return self.__lid


class RemoteFeed(RemotePoint):
    """
    Helper object for Feed Subscription.

    A subscription the connection you have to another Thing's feed. This object allows you to simulate a feed being
    received by your Thing and also to return you the last known received feed data.

    When you subscribe to a Feed this object will be returned from :doc:`IoticAgent.IOT.Thing` Thing.follow. This
    helper object provides `simulate()` and `get_last()`
    """

    def get_last(self):
        """
        Returns:
            None if no recent data is available for this point or a dict.

        Dict contains:

        ::

            'data' # (decoded or raw bytes)
            'mime' # (None, unless payload was not decoded and has a mime type)
            'time' # (datetime representing UTC timestamp of share)

        Note:
            Shorthand for get_recent(1).
        """
        try:
            return next(self.get_recent(1))
        except StopIteration:
            pass

    def get_recent(self, count):
        """
        Get the last instance(s) of feeddata from the feed. Useful if the remote Thing doesn't publish very often.

        Returns:
            An iterable of dicts (in chronologically ascending order) containing

        ::

            'data' # (decoded or raw bytes)
            'mime' # (None, unless payload was not decoded and has a mime type)
            'time' # (datetime representing UTC timestamp of share)

        Args:
            count (integer): How many recent instances to retrieve. High values might be floored to a maximum as defined
                by the container.

        Note:
            Feed data is iterable as soon as it arrives, rather than when the request completes.
        """
        queue = Queue()
        evt = self.get_recent_async(count, queue.put)
        timeout_time = monotonic() + self._client.sync_timeout

        while True:
            try:
                yield queue.get(True, .1)
            except Empty:
                if evt.is_set() or monotonic() >= timeout_time:
                    break
        # Forward any remaining samples which arrived e.g. during this thread being inactive
        try:
            while True:
                yield queue.get_nowait()
        except Empty:
            pass

        self._client._except_if_failed(evt)

    def get_recent_async(self, count, callback):
        """
        Similar to `get_recent` except instead of returning an iterable, passes each dict to the given function which
        must accept a single argument.

        Returns:
            The request.

        Args:
            callback (function): instead of returning an iterable, pass each dict (as described above) to the given
                function which must accept a single argument. Nothing is returned.
        """
        validate_nonnegative_int(count, 'count')
        Validation.callable_check(callback, allow_none=True)
        evt = self._client._request_sub_recent(self.subid, count=count)
        self._client._add_recent_cb_for(evt, callback)
        return evt

    def simulate(self, data, mime=None):
        """
        Simulate the arrival of feeddata into the feed.  Useful if the remote Thing doesn't publish
        very often.

        Args:
            data: The data you want to use to simulate the arrival of remote feed data
            mime (string, optional): The mime type of your data. See: :doc:`IoticAgent.IOT.Point` Feed.share
        """
        self._client.simulate_feeddata(self.__pointid, data, mime)


class RemoteControl(RemotePoint):
    """
    Helper object for Control Subscription.
    A subscription the connection you have to another Thing's control.  This object allows you to pass data
    to the other Things control in two ways, `ask` and `tell`:

    `ask` where you "fire and forget" - the receiving object doesn't have to let you know whether it has actioned your
    request

    `tell` where you expect the receiving object to let you know whether or not has actioned your request

    When you attach to a Control this object will be returned from :doc:`IoticAgent.IOT.Thing` Thing.attach.
    """

    def get_template(self):
        """
        Retreive :doc:`IoticAgent.IOT.PointValueHelper` PointDataObject instance to use with this control.
        """
        return self._client._get_point_data_handler_for(self).get_template()

    def ask(self, data, mime=None):
        """
        Request a remote control to do something.  Ask is "fire-and-forget" in that you won't receive
        any notification of the success or otherwise of the action at the far end.

        Raises:
            IOTException: Infrastructure problem detected
            LinkException: Communications problem between you and the infrastructure

        Args:
            data: The data you want to share
            mime (string, optional): The mime type of the data you're sharing. See: :doc:`IoticAgent.IOT.Point`
                Feed.share)
        """
        evt = self.ask_async(data, mime=mime)
        self._client._wait_and_except_if_failed(evt)

    def ask_async(self, data, mime=None):
        logger.info("ask() [subid=%s]", self.subid)
        if mime is None and isinstance(data, PointDataObject):
            data = data.to_dict()
        return self._client._request_sub_ask(self.subid, data, mime)

    def tell(self, data, timeout=10, mime=None):
        """
        Order a remote control to do something.  Tell is confirmed in that you will receive
        a notification of the success or otherwise of the action at the far end via a callback

        **Example**

        ::

            data = {"thermostat":18.0}
            retval = r_thermostat.tell(data, timeout=10, mime=None)
            if retval is not True:
                print("Thermostat not reset - reason: {reason}".format(reason=retval))

        Returns:
            True on success or else returns the reason (string) one of:

        ::

            "timeout"     # The request-specified timeout has been reached.
            "unreachable" # The remote control is not associated with an agent
                          #     or is not reachable in some other way.
            "failed"      # The remote control indicates it did not perform
                          #     the request.

        Raises:
            IOTException: Infrastructure problem detected
            LinkException: Communications problem between you and the infrastructure

        Args:
            data: The data you want to share
            timeout (int, optional): Default 10.  The delay in seconds before your tell request times out
            mime (string, optional): See: :doc:`IoticAgent.IOT.Point` Feed.share
        """
        evt = self.tell_async(data, timeout=timeout, mime=mime)
        # No point in waiting longer than supplied timeout (as opposed to waiting for sync timeout)
        try:
            self._client._wait_and_except_if_failed(evt, timeout=timeout)
        except IOTSyncTimeout:
            return 'timeout'
        return True if evt.payload['success'] else evt.payload['reason']

    def tell_async(self, data, timeout=10, mime=None):
        """
        Asyncronous version of :doc:`IoticAgent.IOT.RemotePoint` RemoteControl.tell.

        Note:
            payload contains the success and reason keys they are not separated out as in the synchronous version
        """
        logger.info("tell(timeout=%s) [subid=%s]", timeout, self.subid)
        if mime is None and isinstance(data, PointDataObject):
            data = data.to_dict()
        return self._client._request_sub_tell(self.subid, data, timeout, mime=mime)
