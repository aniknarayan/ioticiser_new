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
"""
Iotic Agent In Brief
--------------------
The `IoticAgent` module is the route from your code to Iotic Space. There's a
simple API built around concepts similar to those used in social networking for
humans.  For example, you can `follow` someone else's feed and `share` your own.

This brief guide shows a quick way to get started coding.  It does not attempt to be
an exhaustive introduction to all the code. Follow the links on the left to see more detail.

Getting Started - Installation
------------------------------
The **simplest installation guide** is the
`README on GitHub <https://github.com/Iotic-Labs/py-IoticAgent/blob/master/README.md>`_.

Head there now to install, then come back here.

Getting Started - Environment - Note on PYTHONPATH
--------------------------------------------------
If you install from Git, or use an advanced pip install technique, you will need to be careful that PYTHONPATH is set to
where you've installed the IoticAgent and any dependencies.

* If you used pip to install from PyPI and *didn't* specify a directory in which to install, you don't need to do
  anything.
* If you cloned github or used pypi with the `-t` option, then you'll need to tell python where to look for the modules
  you've installed. See the Install from Git instructions `on GitHub <https://github.com/Iotic-Labs/py-IoticAgent>`_

Coding - Minimum script
-----------------------
Create a new Python script in the src directory with the following lines. This is the minimal Iotic Agent. Let's call it
`my_script.py` for now.

::

    from IoticAgent import IOT
    with IOT.Client() as client:
        pass

You can, if you want, specify the config file in the call to `Client()`

::

    from IoticAgent import IOT
    with IOT.Client(config="my_script.ini") as client:
        pass

More details: :doc:`IoticAgent.IOT.Client`

Coding - Initialisation (ini) file
----------------------------------
If you run this script on its own it will cause an exception on start with a helpful message:

::

    Exception: Minimum configuration for IoticAgent is epId, passwd and token

Create or download from the Iotic Space website file `new_agent/src/my_script.ini` with contents

::

    [agent]
    epid = x
    passwd = y
    token = z

Where x, y and z are the epid, passwd and token from your owner.

Coding - Running your script
----------------------------
::

    $ python3 my_script.py

The minimum script will connect and then wait for incoming messages.
CTRL+C will stop it, as it's not very useful at the moment.

Coding - Logging
----------------
The IoticAgent uses the Python logging module to raise messages to the user.
Most of these you can ignore and, by default, no logging is shown.
To setup logging in your script add the following lines **at the top** of your minimal agent.

::

    import logging
    logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                        level=logging.WARNING)

This will show Warning, Error and Critical messages only.  The next most verbose level is `logging.INFO` which is used
to show functions you've called and any extra information a human user might like for normal development.
There is one more level of logging (`logging.DEBUG`) which shows all the information about everything which
will be too verbose for most people.

Coding - Wiring up the `catchall` callback
------------------------------------------
When feeddata arrives at your minimal Agent it will show a message at logging.WARNING level like:

::

    Received Feed Data for Point GUID <long-string-of-numbers> but no callback registered."

The IoticAgent.IOT.Client provides a `catchall` feature for incoming feed data and control request messages
that you haven't got round to wiring up yet.

::

    def catchall_feeddata(data):
        print("catchall_feeddata:", data)

    with IOT.Client(config="my_script.ini") as client
        client.register_catchall_feeddata(catchall_feeddata)

Anytime any feed data arrives at this Agent the `callback_feeddata` (or whatever you want to call it)
function will be called.

Note:
    `client.reqister_callback_controlreq(fn)` works the same way for control requests.

More details: :doc:`IoticAgent.IOT.Client`

Coding - Make a thing
---------------------
You can create a thing programmatically by calling `create_thing()` on your client instance.  This method returns
an iotic thing object which you should keep for future use.

::

    thing_solar_panels = client.create_thing("SolarPanels")

This will create you a thing with a `"local id"` of `SolarPanels`.  Think of the `local id` as a nickname for your thing
It is for your use only and only on the container where your created it.
No-one else on the system will know this name, be able to search for it or use it.

You can give your thing more descriptive information - see `Describe your things and feeds in metadata` below

More details: :doc:`IoticAgent.IOT.Client`

Coding - Create a feed on your thing
------------------------------------
Now's the time to get your thing to advertise its wares.  Call `create_feed()` on your thing instance
and give it a `local id`.  the same rules apply about this `local id` as before.  Keep the returned iotic
feed object for use later.

::

    feed_current_values = thing_solar_panels.create_feed("Current Values")

More details: :doc:`IoticAgent.IOT.Thing`

Coding - Share data from your feed
----------------------------------
Ok, now to the good bit.  Your code can now scurry off to find some values to share.  Call `share()` on your feed
instance.  In our example the solar panels' current values feed shares a python dictionary of timestamp, power, current,
voltage, and temperature

::

    current_values = {}
    current_values["timestamp"] = datetime.datetime.now().isoformat()
    current_values["power"] = panels.power
    current_values["current"] = panels.current
    current_values["voltage"] = panels.voltage
    current_values["temperature"] = panels.temperature

    feed_current_values.share(current_values)

You can share pretty much what you like: strings, bytes, dictionaries, json and the Agent will
try to bundle it up for you.  You can be assured that whatever you share will come out "the other end" in the same
format: share a dict; they get a dict, etc.

More details: :doc:`IoticAgent.IOT.Point`

Coding - Following someone else's feed
--------------------------------------
To follow someone else's feed, first you need to know the feed's `Globally Unique ID` or `GUID`.  You can get this by
searching the space on the web UI or they could email it to you.  Then you call `follow()` on your thing object for
their remote feed.
You'll also have to specify the callback function you want the agent to call for you when they next publish that feed.

::

    # Args is a dict containing data and other details. See Thing.follow() for more information.
    def feeddata_cb(args):
        print("feeddata_cb", args['data'])

    r_current_values_GUID = "long-string-of-numbers"  # other feed's GUID
    r_feed_current_values = thing_solar_panels.follow(r_current_values_GUID,
                                                      callback=feeddata_cb)

More details: :doc:`IoticAgent.IOT.Thing`

Coding - Simulating someone else's feed
---------------------------------------
You might be wondering why you want to remember the RemoteFeed object (`r_feed_current_values` in the code).
This can be useful if they don't publish often and you want to simulate their publishes in your code for testing.

Call `simulate()` on the remote feed object like so:

::

    try:
        r_feed_current_values.simulate()
    except Exception:
        pass  # didn't have anything to simulate

Your callback function will be called with the last value that was received. The `try/except` block is necessary as
`simulate()` will raise an exception if it's got nothing to simulate - normally because you've never received anything
and it can't just make something up.

More details: :doc:`IoticAgent.IOT.RemotePoint`

Coding - Following one of your own feeds
----------------------------------------
For anything to do with your own things, feeds and controls you can refer to them by their `nickname`.  So to follow a
feed on one of your own things, call `follow()` with the a tuple containing the nicknames of your thing/feed and your
callback.

::

    thing_solar_panels_receiver.follow(("SolarPanels","Current Values"),
                                        callback=feeddata_cb)

More details: :doc:`IoticAgent.IOT`

Coding - Describe your things and feeds in metadata
---------------------------------------------------
The Iotic infrastructure makes great use of semantic metadata to provide meaning for your things, Points and your
Points' values. You can get a metadata helper object from your Thing (or Feed) and describe the Thing in more detail.
The label and description fields are free-text searchable so put information in them that will help others to find them.
The geo-location of your Thing is used if others perform a location-based search.

Note:
    Your metadata is only searchable by others if you call `IoticAgent.IOT.Thing.Thing.set_public`. This allows you some
    granularity on what you choose to make available to others.

::

    #!python
    with thing_solar_panels.get_meta() as meta_thing_solar_panels:
        meta_thing_solar_panels.set_label("Mark's Solar Panels")
        meta_thing_solar_panels.set_description("Solar Array 3.3kW")
        meta_thing_solar_panels.set_location(52.1965071,0.6067687)

    # Optionally set the Thing to be public so that others can search for it.
    thing_solar_panels.set_public()

More details:

* :doc:`IoticAgent.IOT.Thing`
* :doc:`IoticAgent.IOT.ThingMeta`

Coding - Describe the contents of your feed in metadata
-------------------------------------------------------
One of the most useful things you can do in metadata is to let the receiving parties of your feed data know what the
contents of your feed are and their data type and units. There are a couple of extra, helpful modules you can import
from the IoticAgent **at the top of your code**:

::

    from IoticAgent import IOT, Units, Datatypes

Then you can specify the contents of your feed in more explicit detail.  Call `create_value()` on your feed object.

::

    feed_current_values.create_value("timestamp", Datatypes.DATETIME,
                                     "en", "time of reading")
    feed_current_values.create_value("power", Datatypes.DECIMAL,
                                     "en", "output power in watts",
                                     Units.WATT)
    feed_current_values.create_value("current", Datatypes.DECIMAL,
                                     "en", "dc current in amps",
                                     Units.AMPERE)
    feed_current_values.create_value("voltage", Datatypes.DECIMAL,
                                     "en", "dc potential in volts",
                                     Units.VOLT)
    feed_current_values.create_value("temperature", Datatypes.DECIMAL,
                                     "en", "array temperature in celsius",
                                      Units.CELSIUS)

More details: :doc:`IoticAgent.IOT.Point`

Coding - Create a control on your Thing
---------------------------------------
You can also make your Thing respond to activation requests by creating a `control` and its associated callback.  Call
`create_control` on your Thing object.  A control like the opposite of a feed. It's a way that other Things can send
you data or ask your Thing to perform some action(s).

::

    def reset_callback(args):
        print("resetting counters")
        panels.zero_counters()

    thing_solar_panels.create_control("Reset Counters", reset_callback)

When somebody else activates your control with an `ask()` or `tell()`, then your callback will be called.

`args` is a dict containing control data and other details.
See :doc:`IoticAgent.IOT.Thing` for more information.


Coding - Attaching to a remote control
--------------------------------------
Attaching to a remote control is a bit like `following`-ing a feed, except the functions is `attach()` on the remote
Thing. Once you've attached, you can call `ask()` or `tell()` on your RemoteControl object.

::

    r_counters_GUID = "long-string-of-numbers"  # GUID of remote control
    r_control_counters = thing_solar_panels.attach(r_counters_GUID)
    ...
    r_control_counters.ask(<payload>)  #activate the remote control

The two similar functions `ask()` and `tell()` differ in that `ask()` is doesn't require a confirmation that the
action has been done, but `tell()` has a callback to be informed when the far end has done the action and a time-out so
you can be informed if they haven't done it in the time you require.

As you might expect, the `attach` function works for controls on Things you own. Use the tuple of
`(thing_nickname,control_nickname)` to identify the control instead of the GUID

Coding - Which Exceptions
-------------------------
Parameters are validated on request and raise built-in ValueError.

Network failures raise `IoticAgent.Core.Exceptions.LinkException` which can be imported from IoticAgent.IOT.Exceptions
for convenience.

If a request response from Iotic Space contains (FAILED)

`IoticAgent.IOT.Exceptions.IOTUnknown` (Unknown resource EG Thing not found)

`IoticAgent.IOT.Exceptions.IOTMalformed` (Not allowed resource, malformed request)

`IoticAgent.IOT.Exceptions.IOTInternalError` (Container internel error)

`IoticAgent.IOT.Exceptions.IOTAccessDenied` (ACL restriction)
"""

# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Note: needed for pdoc to build index
from . import Units  # NOQA
from . import Datatypes  # NOQA
from . import IOT  # NOQA
from . import Core  # NOQA
from .ThingRunner import ThingRunner, RetryingThingRunner, RunContext  # NOQA
