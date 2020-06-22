

from __future__ import unicode_literals

import json
import requests
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s,%(msecs)03d %(levelname)s [%(name)s] {%(threadName)s} %(message)s',
                    level=logging.WARNING)

# Iotic imports ---------------------------

from IoticAgent import Datatypes
from IoticAgent.Core.compat import monotonic
from IoticAgent.Core.Const import R_FEED
from IoticAgent.Core.Validation import VALIDATION_META_LABEL, VALIDATION_META_COMMENT

from Ioticiser import SourceBase


REFRESH_TIME = 10
LANG = 'en'

# CLASS APIRequester --------------------------------------------------------------------------------------

class APIRequester(object):
    '''
        This class manages the calls to any API
    '''

    @classmethod
    def call_api(cls, fname, apiurl):
        url = apiurl
        try:
            rls = requests.get(url)
            rls.raise_for_status()
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("__call_api error: %s", str(exc))
        logger.debug("__call_api name=%s url=%s, status_code=%s", fname, url, rls.status_code)
        if rls.ok:
            fdata = rls.text
            return json.loads(fdata)
        else:
            logger.error("__call_api error %i", rls.status_code)


# CLASS Weather ---------------------------------------------------------------------------------------------

class Weather(object):  # pylint: disable=too-many-instance-attributes
    """
        Stores weather's entity information.
        This class also contains all the needed keys for parsing the JSON file.
    """

    # Basic info
    __key_name = 'name'  

    # Feeds
    __key_temp = 'temp'
    __key_humidity = 'humidity'
    

    def __init__(self, json_file):

        # Weathers's info
        self.name = str(json_file[self.__key_name])       
        
        # Weather's Feeds
        self.temp = str(json_file[self.__key_temp])
        self.humidity = str(json_file[self.__key_humidity])

        # Compose a Loaction name abbreviation
        trimmed_name = self.name.strip()        
        self.abbr = trimmed_name


# CLASS SchoolsPublisher ---------------------------------------------------------------------------------------------

class WeatherPublisher(SourceBase):
    """
        Creates and publish San Francisco's schools data
        This class transform each school object into Iotic Thing.
    """

    __license_notice = ('Obtained from openweather')
    __opendata_weather_url = 'http://api.openweathermap.org/data/2.5/weather?q=Bangalore'
    __prefix = 'weather_'
    __user_app_key = True

    def __init__(self, stash, config, stop):

        super(WeatherPublisher, self).__init__(stash, config, stop)
        self.__limit = None
        self.__refresh_time = REFRESH_TIME
        self.__validate_config()

    def __validate_config(self):

        if 'app_key' not in self._config:
            msg = "No app_key set, openweathermap app key is mandatory to fetch weather data."
            logger.error(msg)
            self.__use_app_key = False
         
        if 'format_limit_things' in self._config:
            self.__limit = int(self._config['format_limit_things'])
        if 'refresh_time' in self._config:
            self.__refresh_time = float(self._config['refresh_time'])

    def get_weather_from_API(self):
        
        full_opendata_weather_url = self.__opendata_weather_url
        if self.__use_app_key is True:
            full_opendata_weather_url += "&appid=" + self._config['app_key']
        data = APIRequester.call_api('opendata_weather', full_opendata_weather_url)
        if data is not None:
            self.__parse_opendata_weather_format(data)

    # PARSE DATA ------------------------------------------------------------------------------------------------

    @classmethod
    def _set_thing_attributes(cls, weather, thing):
        """
            Sets Thing's label and set tags
            Makes Thing public
        """
        label = weather.name.replace('\n', ' ').replace('\r', '').strip()        
        thing.set_label(label, LANG)
        thing.create_tag(['WeatherData', 'Bangalore', 'OpenData', 'openweathermap'])
        
        thing.set_public(public=True)

    def _set_thing_description(self, weather, thing):

        description = weather.name + "'s Weather data. "        

        description += self.__license_notice
        description = description[:VALIDATION_META_COMMENT].strip()  # todo? ensure length
        thing.set_description(description, LANG)

    @classmethod
    def _set_thing_points(cls, weather, thing):
        """
            Creates, defines and publish thing's feed
            Uses two weather's values as feed: Temp and Humidity
        """
        point = thing.create_point(R_FEED, weather.abbr)
        point.set_label(weather.abbr + ' Weather', LANG)
        point.set_description('Weather Data', LANG)
        point.create_value('temp',
                           vtype=Datatypes.FLOAT,
                           description='Temperature',
                           data=weather.temp)
        point.create_value('humidity',
                           vtype=Datatypes.FLOAT,
                           description='Humidity',
                           data=weather.humidity)
       
        point.set_recent_config(max_samples=-1)
        point.share()

    def __parse_opendata_weather_format(self, data):
        """
            Uses json data to create weather objects.
            Builds weather's thing with the information they have
        """

        for json_weather in data:

            weather = Weather(json_weather)

            # We need a unique name for the thing
            thing_name = self.__prefix + weather.abbr

            with self._stash.create_thing(thing_name) as thing:

                self._set_thing_attributes(weather, thing)
                self._set_thing_description(weather, thing)
                self._set_thing_points(weather, thing)

            logger.info('Created ' + thing_name)

    # RUN ---------------------------------------------------------------------------------------------------

    def run(self):        
        while True:
            self.get_weather_from_API()
            if self._stop.wait(timeout= self.__refresh_time):
                break
            self._stop.wait(timeout=5)

    # def run(self):
    #     if self.__get_some_data():
    #         self.__publish_some_stuff()
    #     else:
    #         logger.info("Nothing to do - new data not available")

    #     logger.info("Finished")
