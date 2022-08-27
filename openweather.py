import os
import requests
import datetime
import pytz
import time
import collections
import pprint
from builtins import AssertionError
import logging

logger = logging.getLogger(__name__)


pprinter = pprint.PrettyPrinter


class Conditions:
    def __init__(self, clouds, dew_point, feels_like, humidity, pressure, uvi, weather, wind_deg, wind_speed):
        self.created_at = time.time()
        self.clouds = clouds
        self.dew_point = dew_point
        self.feels_like = feels_like
        self.humidity = humidity
        self.pressure = pressure
        self.uvi = uvi
        self.description = weather
        self.wind_deg = wind_deg
        self.wind_speed = wind_speed


class Daylight:
    def __init__(self, sunrise, sunset):
        self.sunrise = sunrise
        self.sunset = sunset


class ChancePrecipitation:
    def __init__(self, pop):  # Probability of Precipitation
        self.pop = pop


class VolatileConditions:
    def __init__(self, temperature, visibility, rain_last_hour, snow_last_hour):
        self.temperature = temperature
        self.visibility = visibility
        self.last_hour_rain = rain_last_hour
        self.last_hour_snow = snow_last_hour


# ==========================================================================================================================

# class Weather:
#     def __init__(self, conditions: Conditions):
#         self.conditions = conditions
#
#     @staticmethod
#     def kelvin_to_fahrenheit(kelvin: float):
#         fahrenheit = ((kelvin - 273.15) * 1.8 + 32)
#         return fahrenheit

class CurrentWeather(Conditions, Daylight, VolatileConditions):
    def __init__(self, rain, snow, conditions, daylight, volatile_conditions):
        self.last_hour_rain = rain
        self.last_hour_snow = snow
        Conditions.__init__(self, *conditions)
        Daylight.__init__(self, *daylight)
        VolatileConditions.__init__(self, *volatile_conditions)
    # def __init__(self, rain, snow, *args, **kwargs):
    #     super(CurrentWeather, self).__init__(rain, snow, *args, **kwargs)


class HourlyWeather(Conditions, ChancePrecipitation, VolatileConditions):
    def __init__(self, forecast_for_time, conditions, chance_precip, volatile_conditions):
        # super(HourlyWeather, self).__init__(forecast_for_time, *args, **kwargs)
        self.forecast_for_time = forecast_for_time
        Conditions.__init__(self, *conditions)
        ChancePrecipitation.__init__(self, *chance_precip)
        VolatileConditions.__init__(self, *volatile_conditions)


class DailyWeather(Conditions, Daylight, ChancePrecipitation):
    def __init__(self, temp_morn, temp_day, temp_eve, temp_night, temp_min, temp_max,
                 conditions, daylight, chance_precip, total_rain=0.0, total_snow=0.0):
        self.temp_morn = temp_morn
        self.temp_day = temp_day
        self.temp_eve = temp_eve
        self.temp_night = temp_night
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.total_rain = total_rain
        self.total_snow = total_snow
        Conditions.__init__(self, *conditions)
        Daylight.__init__(self, *daylight)
        ChancePrecipitation.__init__(self, *chance_precip)
# ==========================================================================================================================


class OpenweatherController:

    def __init__(self, lat=44.95, lon=-93.29):  # default coordinates for 55408, note negative lon value (otherwise results are for the Gobi Desert)
        self.api_key = os.getenv('openweather_api_key')
        self.latitude = lat
        self.longitude = lon
        self.latest_response_time = None
        self.latest_response_data = None

    def verify_or_get_data(self):
        """
        Only make new API call if data is over 1 hour old.
        :return: bool
        """
        current_time = time.time()

        if self.latest_response_data is None or self.latest_response_data == {}:
            self.latest_response_data = self.call_api()
            self.latest_response_time = current_time
            self.verify_or_get_data()
            return True

        elif current_time - self.latest_response_time > 3600:  # if difference between now and latest response is more than 3600sec (1 hour)
            self.latest_response_data = self.call_api()
            self.latest_response_time = current_time
            self.verify_or_get_data()
            return True

        elif current_time - self.latest_response_time <= 3600:
            return True

        else:
            return False

    def call_api(self) -> dict:
        try:
            endpoint = f'https://api.openweathermap.org/data/2.5/onecall?lat={self.latitude}&lon={self.longitude}&appid={self.api_key}'
            response_dict = requests.get(endpoint).json()
            print(f'response_dict.keys() in call_api = {response_dict.keys()}')
            pprint.pprint(response_dict)
            return response_dict
        except requests.exceptions.Timeout:
            return {}

    def dispatch(self, statement):

        # verify_data_currency() call api controller in main to verify

        if not self.verify_or_get_data():
            # TODO log, signal, notify user
            print('unable to verify or get weather data')
            return None

        current_weather_phrases = ("what's the weather right now", "current weather", "what's it like outside", "what's the weather like", "tell me the weather", "is it hot out", "is it cold out")
        hourly_forecast_phrases = ("what's the hourly weather", "what's the hourly forecast", "six hour forecast", "hourly forecast")
        todays_weather_phrases = ("what's the weather like today", "what's the weather today", "today's weather", "weather for the rest of the day", "tell me today's weather", "is it going to rain", "is it going to snow", "is it going to storm", "is it cold today", "is it hot today")
        three_day_forecast_phrases = ('three day forecast', "what's the weather like the next couple of days", "forecast for three days")
        weekly_forecast_phrases = ("upcoming weather", "weekly forecast", "what's the forecast", "is it going to rain this week", "is it going to snow this week", "what's the weather like this week", "this weeks forecast")

        commands = {
            current_weather_phrases: self.get_current_report,
            hourly_forecast_phrases: self.get_hourly_report,
            todays_weather_phrases: self.get_daily_report,
            three_day_forecast_phrases: self.get_daily_report,
            weekly_forecast_phrases: self.get_daily_report
        }

        keywords = {}
        function_call = None
        for command_set in commands:
            if statement in command_set:
                function_call = commands[command_set]
                if command_set == todays_weather_phrases:
                    keywords = {'num_days': 1}
                elif command_set == three_day_forecast_phrases:
                    keywords = {'num_days': 3}
                elif command_set == weekly_forecast_phrases:
                    keywords = {'num_days': 8}
        if function_call:
            response_script = function_call(**keywords)
            return response_script
        else:
            print(f'type(function_call) = {type(function_call)}')
            return None

    def get_current_report(self):
        valid, msg = self.validate_response_data()
        if not valid:
            return msg
        current_weather = self.parse_current()
        current_temp_fnht = int(self.kelvin_to_fahrenheit(current_weather.temperature))
        feels_like_fnht = int(self.kelvin_to_fahrenheit(current_weather.feels_like))
        current_report = f"currently it is {current_weather.description} and {current_temp_fnht} degrees," \
                         f" with a real feel of {feels_like_fnht} degrees."
        if current_weather.last_hour_snow > 0.0:
            current_report += f" snowfall totalled {current_weather.last_hour_snow} millimeters in the last hour."
        if current_weather.last_hour_rain > 0.0:
            current_report += f" rainfall totalled {current_weather.last_hour_rain} millimeters in the last hour."
        return current_report

    def get_hourly_report(self, hours=6):
        valid, msg = self.validate_response_data()
        if not valid:
            return msg
        tts_message = ''
        hourly_forecasts = self.parse_hourly_forecasts()
        forecast_count = 0
        for forecast in hourly_forecasts:
            if forecast_count < hours:
                hour = epoch_to_hour(forecast.forecast_for_time)
                temp = round(self.kelvin_to_fahrenheit(forecast.temperature))
                feels_like = round(self.kelvin_to_fahrenheit(forecast.feels_like))
                description = forecast.description
                pop = forecast.pop
                pop_msg = self.get_pop_message(pop, temp)
                hourly_report = f" {hour} will be {description} and {temp} degrees with a real feel of {feels_like} degrees, {pop_msg}."
                tts_message += hourly_report
                forecast_count += 1
                print(f'forecast_count = {forecast_count}, hours = {hours}')
        return tts_message

    def get_daily_report(self, num_days=1):
        valid, msg = self.validate_response_data()
        if not valid:
            return msg
        try:
            assert num_days in range(1, 9)  # can only request forecast for no less than 1 day, and no more than 8
            daily_forecasts = self.parse_daily_forecasts()
            forecast_count = 0
            tts_message = ''
            for forecast in daily_forecasts:
                if forecast_count < num_days:
                    for_time = daily_forecasts[forecast]
                    forecast_day = 'today' if forecast_count == 0 else epoch_to_day(for_time)
                    temp_min = round(self.kelvin_to_fahrenheit(forecast.temp_min))
                    temp_max = round(self.kelvin_to_fahrenheit(forecast.temp_max))
                    rain = forecast.total_rain
                    snow = forecast.total_snow
                    pop = forecast.pop
                    precip_msg = self.get_daily_precip_msg(pop, rain, snow)
                    description = forecast.description
                    daily_msg = f'{forecast_day} will be {description} with a low of {temp_min} degrees and a high of {temp_max} degrees, {precip_msg}.'
                    tts_message += daily_msg
                    forecast_count += 1
                else:
                    break
            return tts_message

        except AssertionError as error:
            logger.log(level=logging.ERROR, msg=error)

    @staticmethod
    def get_daily_precip_msg(pop, rain, snow):
        tts_message = ''
        if rain > 0:
            tts_message += f' rain totaling {rain} millimeters '

        if rain > 0 and snow > 0:
            tts_message += 'and'

        if snow > 0:
            tts_message += f' snow totaling {snow} millimeters'

        tts_message += f' with a {pop} percent chance of precipitation.'

        return tts_message

    @staticmethod
    def get_pop_message(pop, temp):
        message = ''
        if pop > 0:
            message = f'and a {pop} percent chance of '
            if temp > 31:
                message += 'rain'
            elif temp <= 31:
                message += 'snow'
        return message

    @staticmethod
    def parse_conditions(data: dict):
        """
        :param data: api_response_dict["current"] OR api_response_dict["hourly"] OR api_response_dict["daily"]
        :return: list
        """
        weather_data = [data['clouds'], data['dew_point'], data['feels_like'], data['humidity'], data['pressure'], data['uvi'],
                        data['weather'][0]['description'], data['wind_deg'], data['wind_speed']]
        return weather_data

    @staticmethod
    def parse_volatile_conditions(data: dict):
        """
        :param data: api_response_dict["current"] OR api_response_dict["hourly"]
        :return: VolatileConditions
        """
        rain_data = data['rain'] if 'rain' in data else 0.0
        snow_data = data['snow'] if 'snow' in data else 0.0
        volatile_conditions_data = [data['temp'], data['visibility'], rain_data, snow_data]
        return volatile_conditions_data

    @staticmethod
    def parse_daylight(data: dict):
        """
        :param data:  api_response_dict["current"] OR api_response_dict["daily"]
        :return: Daylight
        """
        daylight_data = [data['sunrise'], data['sunset']]
        # new_daylight = Daylight(sunrise=data['sunrise'], sunset=data['sunset'])
        return daylight_data

    @staticmethod
    def parse_chance_precipitation(data: dict):
        """
        :param data: api_response_dict["hourly"] OR api_response_dict["daily"]
        :return: ChancePrecipitation
        """
        new_chance_precipitation = [data['pop']]
        return new_chance_precipitation

    # @staticmethod
    # def rain_data(data: dict) -> (bool, float):
    #     """
    #     :param data: api_response_dict["hourly"] OR api_response_dict["daily"]
    #     :return: bool
    #     """
    #     if 'rain' in data:
    #         return True, data['rain']
    #     else:
    #         return False, 0.0
    #
    # @staticmethod
    # def snow_data(data: dict) -> float:
    #     if 'snow' in data:
    #         return data['snow']
    #     else:
    #         return 0.0

    @staticmethod
    def kelvin_to_fahrenheit(kelvin: float):
        fahrenheit = ((kelvin - 273.15) * 1.8 + 32)
        return fahrenheit

    def parse_current(self):
        current_weather_data = self.latest_response_data['current']
        rain_total = current_weather_data['rain'] if 'rain' in current_weather_data else 0.0
        snow_total = current_weather_data['snow'] if 'snow' in current_weather_data else 0.0
        current_conditions = self.parse_conditions(current_weather_data)
        current_daylight = self.parse_daylight(current_weather_data)
        current_volatile = self.parse_volatile_conditions(current_weather_data)
        current_weather = CurrentWeather(rain=rain_total, snow=snow_total, conditions=current_conditions,
                                         daylight=current_daylight, volatile_conditions=current_volatile)
        return current_weather

    def parse_hourly_forecasts(self) -> {dict}:
        """
        return a dict of 48 dicts, one forecast for each of the next 48 hours, keys are unix timestamps designating the hour
        :return:
        """
        hourly_forecasts = []
        hourly_weather_data = self.latest_response_data['hourly']
        print(f'type(hourly_weather_data) = {type(hourly_weather_data)}')
        for hour_data in hourly_weather_data:
            print(f'type(hour_data) = {type(hour_data)}')
            print(f'hour_data.keys() = {hour_data.keys()}')
            print(f'type(hour_data["dt"]) = {type(hour_data["dt"])}')
            print(f'hour_data["dt"] = {hour_data["dt"]}')
            for_time = hour_data['dt']

            hourly_conditions = self.parse_conditions(hour_data)
            hourly_chance_precipitation = self.parse_chance_precipitation(hour_data)
            hourly_volatile = self.parse_volatile_conditions(hour_data)
            new_hourly_forecast = HourlyWeather(forecast_for_time=for_time, conditions=hourly_conditions,
                                                chance_precip=hourly_chance_precipitation, volatile_conditions=hourly_volatile)
            hourly_forecasts.append(new_hourly_forecast)
        return hourly_forecasts

    def parse_daily_forecasts(self) -> {dict}:
        daily_forecasts = collections.OrderedDict()
        daily_weather_data = self.latest_response_data['daily']

        for daily_data in daily_weather_data:
            for_time = daily_data['dt']
            daily_conditions = self.parse_conditions(daily_data)
            daily_daylight = self.parse_daylight(daily_data)
            daily_chance_precipitation = self.parse_chance_precipitation(daily_data)
            temp_morn = daily_data['temp']['morn']
            temp_day = daily_data['temp']['day']
            temp_eve = daily_data['temp']['eve']
            temp_night = daily_data['temp']['night']
            temp_min = daily_data['temp']['min']
            temp_max = daily_data['temp']['max']
            total_rain = daily_data['rain'] if 'rain' in daily_data else 0.0
            total_snow = daily_data['snow'] if 'snow' in daily_data else 0.0

            new_daily_forecast = DailyWeather(temp_morn, temp_day, temp_eve, temp_night, temp_min, temp_max,
                                              total_rain=total_rain,total_snow=total_snow, conditions=daily_conditions,
                                              daylight=daily_daylight, chance_precip=daily_chance_precipitation)

            daily_forecasts[new_daily_forecast] = for_time
        return daily_forecasts

    def validate_response_data(self):
        if self.latest_response_data == {}:
            return False, "unable to retrieve weather data. it has nothing to do with the opus that is this source code, " \
                          "and everything to do with the dark magic of the internet."
        else:
            return True, ""


def get_wind_direction(wind_deg):
    return wind_deg


def epoch_to_datetime(unix_timestamp, timezone='US/Central'):
    tz = pytz.timezone(timezone)
    dt = datetime.datetime.fromtimestamp(unix_timestamp, tz)
    return dt.strftime('%A, %B %d, %I:%M:%S %p')


def epoch_to_day(unix_timestamp, timezone='US/Central'):
    tz = pytz.timezone(timezone)
    date = datetime.datetime.fromtimestamp(unix_timestamp, tz)
    return date.strftime('%A, %B, %d')


def epoch_to_hour(unix_timestamp, timezone='US/Central'):
    tz = pytz.timezone(timezone)
    hour = datetime.datetime.fromtimestamp(unix_timestamp, tz)
    int_hour = int(hour.strftime('%I'))
    am_pm = hour.strftime('%p')
    return f'{int_hour} {am_pm}'
    # return hour.strftime('%I %p')






