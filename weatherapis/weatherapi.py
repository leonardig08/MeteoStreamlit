
import numpy as np
import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
import json
from metpy.calc import supercell_composite, most_unstable_cape_cin, storm_relative_helicity, wind_components, \
    bunkers_storm_motion, bulk_shear
from metpy.units import units
from datetime import datetime

import streamlit as st


def get_condizione_meteo_italiano(wmo_code):
    condizioni_meteo = {
        0: "Cielo sereno",
        1: "Principalmente sereno",
        2: "Parzialmente nuvoloso",
        3: "Coperto",
        45: "Nebbia e nebbia gelida con deposito di galaverna",
        48: "Nebbia gelida con deposito di galaverna",
        51: "Pioggerella leggera",
        53: "Pioggerella moderata",
        55: "Pioggerella forte",
        56: "Pioggerella gelida leggera",
        57: "Pioggerella gelida forte",
        61: "Pioggia leggera",
        63: "Pioggia moderata",
        65: "Pioggia forte",
        66: "Pioggia gelida leggera",
        67: "Pioggia gelida forte",
        71: "Neve leggera",
        73: "Neve moderata",
        75: "Neve forte",
        77: "Gragnola",
        80: "Rovesci di pioggia leggeri",
        81: "Rovesci di pioggia moderati",
        82: "Rovesci di pioggia violenti",
        85: "Rovesci di neve leggeri",
        86: "Rovesci di neve forti",
        95: "Temporale leggero o moderato",
        96: "Temporale con grandine leggera",
        99: "Temporale con grandine forte"
    }
    return condizioni_meteo.get(wmo_code, "Condizione meteorologica non definita")


class ApiWeather:
    def __init__(self):
        self.url = "https://api.open-meteo.com/v1/forecast"
        self.urlgeo = "https://geocoding-api.open-meteo.com/v1/search"
        self.geokey = st.secrets["geo_key"]
        self.params = {}
        self.cacheSession = requests_cache.CachedSession("private/.cache", expire_after=3600)
        self.retrySession = retry(self.cacheSession, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retrySession)
        self.lang = "it"
        self.daily = None
        self.minutely = None

    def requestgeocode(self, searchterm):
        response = self.retrySession.get(f"https://api.geoapify.com/v1/geocode/autocomplete?text={searchterm}&format=json&lang={self.lang}&apiKey={self.geokey}")
        print(response.status_code)
        cnt = json.loads(response.content)
        return [(r["formatted"], (r["lon"], r["lat"], r["timezone"]["name"], r["formatted"])) for r in cnt["results"]]

    #@cache_to_csv("private/cache{i}.csv", refresh_time=3600)
    def requestweather(self, lon, lat, timezone):
        print("Starting request")
        #region Dati
        params = {
            "latitude": lat,
            "longitude": lon,
            "timezone": timezone,
            "daily": ["cape_mean", "cape_max", "temperature_2m_min", "apparent_temperature_mean", "temperature_2m_max", "sunrise", "sunset", "precipitation_probability_max", "uv_index_max"],
	        "hourly": ["temperature_2m", "weather_code", "precipitation_probability", "apparent_temperature", "dew_point_2m", "relative_humidity_2m", "surface_pressure", "temperature_1000hPa", "temperature_925hPa", "temperature_800hPa", "temperature_100hPa", "temperature_250hPa", "temperature_500hPa", "temperature_200hPa", "temperature_400hPa", "temperature_700hPa", "temperature_900hPa", "temperature_975hPa", "temperature_150hPa", "temperature_300hPa", "temperature_600hPa", "temperature_850hPa", "temperature_950hPa", "relative_humidity_1000hPa", "relative_humidity_800hPa", "relative_humidity_925hPa", "relative_humidity_500hPa", "relative_humidity_250hPa", "relative_humidity_100hPa", "relative_humidity_200hPa", "relative_humidity_400hPa", "relative_humidity_700hPa", "relative_humidity_900hPa", "relative_humidity_975hPa", "relative_humidity_150hPa", "relative_humidity_300hPa", "relative_humidity_600hPa", "relative_humidity_850hPa", "relative_humidity_950hPa", "wind_speed_100hPa", "wind_speed_250hPa", "wind_speed_500hPa", "wind_speed_800hPa", "wind_speed_1000hPa", "wind_speed_925hPa", "wind_speed_200hPa", "wind_speed_400hPa", "wind_speed_700hPa", "wind_speed_900hPa", "wind_speed_975hPa", "wind_speed_150hPa", "wind_speed_300hPa", "wind_speed_600hPa", "wind_speed_850hPa", "wind_speed_950hPa", "wind_direction_1000hPa", "wind_direction_925hPa", "wind_direction_500hPa", "wind_direction_250hPa", "wind_direction_100hPa", "wind_direction_800hPa", "wind_direction_400hPa", "wind_direction_200hPa", "wind_direction_900hPa", "wind_direction_700hPa", "wind_direction_975hPa", "wind_direction_600hPa", "wind_direction_150hPa", "wind_direction_300hPa", "wind_direction_850hPa", "wind_direction_950hPa", "geopotential_height_100hPa", "geopotential_height_250hPa", "geopotential_height_500hPa", "geopotential_height_800hPa", "geopotential_height_925hPa", "geopotential_height_1000hPa", "geopotential_height_200hPa", "geopotential_height_400hPa", "geopotential_height_700hPa", "geopotential_height_900hPa", "geopotential_height_975hPa", "geopotential_height_150hPa", "geopotential_height_300hPa", "geopotential_height_600hPa", "geopotential_height_950hPa", "geopotential_height_850hPa", "cloud_cover", "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m", "cape", "lifted_index", "convective_inhibition", "uv_index"],
	        "current": ["temperature_2m", "relative_humidity_2m", "weather_code"],
	        "minutely_15": ["lightning_potential", "weather_code", "temperature_2m", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", "cape", "relative_humidity_2m", "apparent_temperature", "dew_point_2m", "precipitation"],
        }
        responses = self.openmeteo.weather_api(self.url, params=params)
        print("Got data")

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        # print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        # print(f"Elevation {response.Elevation()} m asl")
        elevation = response.Elevation()
        # print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
        # print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Current values. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_relative_humidity_2m = current.Variables(1).Value()
        current_weather_code = current.Variables(2).Value()

        # print(f"Current time {current.Time()}")
        # print(f"Current temperature_2m {current_temperature_2m}")
        # print(f"Current relative_humidity_2m {current_relative_humidity_2m}")
        # print(f"Current weather_code {current_weather_code}")

        # Process minutely_15 data. The order of variables needs to be the same as requested.
        minutely_15 = response.Minutely15()
        minutely_15_lightning_potential = minutely_15.Variables(0).ValuesAsNumpy()
        minutely_15_weather_code = minutely_15.Variables(1).ValuesAsNumpy()
        minutely_15_temperature_2m = minutely_15.Variables(2).ValuesAsNumpy()
        minutely_15_wind_speed_10m = minutely_15.Variables(3).ValuesAsNumpy()
        minutely_15_wind_direction_10m = minutely_15.Variables(4).ValuesAsNumpy()
        minutely_15_wind_gusts_10m = minutely_15.Variables(5).ValuesAsNumpy()
        minutely_15_cape = minutely_15.Variables(6).ValuesAsNumpy()
        minutely_15_relative_humidity_2m = minutely_15.Variables(7).ValuesAsNumpy()
        minutely_15_apparent_temperature = minutely_15.Variables(8).ValuesAsNumpy()
        minutely_15_dew_point_2m = minutely_15.Variables(9).ValuesAsNumpy()
        minutely_15_precipitation = minutely_15.Variables(10).ValuesAsNumpy()

        minutely_15_data = {"date": pd.date_range(
            start=pd.to_datetime(minutely_15.Time(), unit="s", utc=True),
            end=pd.to_datetime(minutely_15.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=minutely_15.Interval()),
            inclusive="left"
        )}

        minutely_15_data["lightning_potential"] = minutely_15_lightning_potential
        minutely_15_data["weather_code"] = minutely_15_weather_code
        minutely_15_data["temperature_2m"] = minutely_15_temperature_2m
        minutely_15_data["wind_speed_10m"] = minutely_15_wind_speed_10m
        minutely_15_data["wind_direction_10m"] = minutely_15_wind_direction_10m
        minutely_15_data["wind_gusts_10m"] = minutely_15_wind_gusts_10m
        minutely_15_data["cape"] = minutely_15_cape
        minutely_15_data["relative_humidity_2m"] = minutely_15_relative_humidity_2m
        minutely_15_data["apparent_temperature"] = minutely_15_apparent_temperature
        minutely_15_data["dew_point_2m"] = minutely_15_dew_point_2m
        minutely_15_data["precipitation"] = minutely_15_precipitation

        minutely_15_dataframe = pd.DataFrame(data=minutely_15_data)

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_weather_code = hourly.Variables(1).ValuesAsNumpy()
        hourly_precipitation_probability = hourly.Variables(2).ValuesAsNumpy()
        hourly_apparent_temperature = hourly.Variables(3).ValuesAsNumpy()
        hourly_dew_point_2m = hourly.Variables(4).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(5).ValuesAsNumpy()
        hourly_surface_pressure = hourly.Variables(6).ValuesAsNumpy()
        hourly_temperature_1000hPa = hourly.Variables(7).ValuesAsNumpy()
        hourly_temperature_925hPa = hourly.Variables(8).ValuesAsNumpy()
        hourly_temperature_800hPa = hourly.Variables(9).ValuesAsNumpy()
        hourly_temperature_100hPa = hourly.Variables(10).ValuesAsNumpy()
        hourly_temperature_250hPa = hourly.Variables(11).ValuesAsNumpy()
        hourly_temperature_500hPa = hourly.Variables(12).ValuesAsNumpy()
        hourly_temperature_200hPa = hourly.Variables(13).ValuesAsNumpy()
        hourly_temperature_400hPa = hourly.Variables(14).ValuesAsNumpy()
        hourly_temperature_700hPa = hourly.Variables(15).ValuesAsNumpy()
        hourly_temperature_900hPa = hourly.Variables(16).ValuesAsNumpy()
        hourly_temperature_975hPa = hourly.Variables(17).ValuesAsNumpy()
        hourly_temperature_150hPa = hourly.Variables(18).ValuesAsNumpy()
        hourly_temperature_300hPa = hourly.Variables(19).ValuesAsNumpy()
        hourly_temperature_600hPa = hourly.Variables(20).ValuesAsNumpy()
        hourly_temperature_850hPa = hourly.Variables(21).ValuesAsNumpy()
        hourly_temperature_950hPa = hourly.Variables(22).ValuesAsNumpy()
        hourly_relative_humidity_1000hPa = hourly.Variables(23).ValuesAsNumpy()
        hourly_relative_humidity_800hPa = hourly.Variables(24).ValuesAsNumpy()
        hourly_relative_humidity_925hPa = hourly.Variables(25).ValuesAsNumpy()
        hourly_relative_humidity_500hPa = hourly.Variables(26).ValuesAsNumpy()
        hourly_relative_humidity_250hPa = hourly.Variables(27).ValuesAsNumpy()
        hourly_relative_humidity_100hPa = hourly.Variables(28).ValuesAsNumpy()
        hourly_relative_humidity_200hPa = hourly.Variables(29).ValuesAsNumpy()
        hourly_relative_humidity_400hPa = hourly.Variables(30).ValuesAsNumpy()
        hourly_relative_humidity_700hPa = hourly.Variables(31).ValuesAsNumpy()
        hourly_relative_humidity_900hPa = hourly.Variables(32).ValuesAsNumpy()
        hourly_relative_humidity_975hPa = hourly.Variables(33).ValuesAsNumpy()
        hourly_relative_humidity_150hPa = hourly.Variables(34).ValuesAsNumpy()
        hourly_relative_humidity_300hPa = hourly.Variables(35).ValuesAsNumpy()
        hourly_relative_humidity_600hPa = hourly.Variables(36).ValuesAsNumpy()
        hourly_relative_humidity_850hPa = hourly.Variables(37).ValuesAsNumpy()
        hourly_relative_humidity_950hPa = hourly.Variables(38).ValuesAsNumpy()
        hourly_wind_speed_100hPa = hourly.Variables(39).ValuesAsNumpy()
        hourly_wind_speed_250hPa = hourly.Variables(40).ValuesAsNumpy()
        hourly_wind_speed_500hPa = hourly.Variables(41).ValuesAsNumpy()
        hourly_wind_speed_800hPa = hourly.Variables(42).ValuesAsNumpy()
        hourly_wind_speed_1000hPa = hourly.Variables(43).ValuesAsNumpy()
        hourly_wind_speed_925hPa = hourly.Variables(44).ValuesAsNumpy()
        hourly_wind_speed_200hPa = hourly.Variables(45).ValuesAsNumpy()
        hourly_wind_speed_400hPa = hourly.Variables(46).ValuesAsNumpy()
        hourly_wind_speed_700hPa = hourly.Variables(47).ValuesAsNumpy()
        hourly_wind_speed_900hPa = hourly.Variables(48).ValuesAsNumpy()
        hourly_wind_speed_975hPa = hourly.Variables(49).ValuesAsNumpy()
        hourly_wind_speed_150hPa = hourly.Variables(50).ValuesAsNumpy()
        hourly_wind_speed_300hPa = hourly.Variables(51).ValuesAsNumpy()
        hourly_wind_speed_600hPa = hourly.Variables(52).ValuesAsNumpy()
        hourly_wind_speed_850hPa = hourly.Variables(53).ValuesAsNumpy()
        hourly_wind_speed_950hPa = hourly.Variables(54).ValuesAsNumpy()
        hourly_wind_direction_1000hPa = hourly.Variables(55).ValuesAsNumpy()
        hourly_wind_direction_925hPa = hourly.Variables(56).ValuesAsNumpy()
        hourly_wind_direction_500hPa = hourly.Variables(57).ValuesAsNumpy()
        hourly_wind_direction_250hPa = hourly.Variables(58).ValuesAsNumpy()
        hourly_wind_direction_100hPa = hourly.Variables(59).ValuesAsNumpy()
        hourly_wind_direction_800hPa = hourly.Variables(60).ValuesAsNumpy()
        hourly_wind_direction_400hPa = hourly.Variables(61).ValuesAsNumpy()
        hourly_wind_direction_200hPa = hourly.Variables(62).ValuesAsNumpy()
        hourly_wind_direction_900hPa = hourly.Variables(63).ValuesAsNumpy()
        hourly_wind_direction_700hPa = hourly.Variables(64).ValuesAsNumpy()
        hourly_wind_direction_975hPa = hourly.Variables(65).ValuesAsNumpy()
        hourly_wind_direction_600hPa = hourly.Variables(66).ValuesAsNumpy()
        hourly_wind_direction_150hPa = hourly.Variables(67).ValuesAsNumpy()
        hourly_wind_direction_300hPa = hourly.Variables(68).ValuesAsNumpy()
        hourly_wind_direction_850hPa = hourly.Variables(69).ValuesAsNumpy()
        hourly_wind_direction_950hPa = hourly.Variables(70).ValuesAsNumpy()
        hourly_geopotential_height_100hPa = hourly.Variables(71).ValuesAsNumpy()
        hourly_geopotential_height_250hPa = hourly.Variables(72).ValuesAsNumpy()
        hourly_geopotential_height_500hPa = hourly.Variables(73).ValuesAsNumpy()
        hourly_geopotential_height_800hPa = hourly.Variables(74).ValuesAsNumpy()
        hourly_geopotential_height_925hPa = hourly.Variables(75).ValuesAsNumpy()
        hourly_geopotential_height_1000hPa = hourly.Variables(76).ValuesAsNumpy()
        hourly_geopotential_height_200hPa = hourly.Variables(77).ValuesAsNumpy()
        hourly_geopotential_height_400hPa = hourly.Variables(78).ValuesAsNumpy()
        hourly_geopotential_height_700hPa = hourly.Variables(79).ValuesAsNumpy()
        hourly_geopotential_height_900hPa = hourly.Variables(80).ValuesAsNumpy()
        hourly_geopotential_height_975hPa = hourly.Variables(81).ValuesAsNumpy()
        hourly_geopotential_height_150hPa = hourly.Variables(82).ValuesAsNumpy()
        hourly_geopotential_height_300hPa = hourly.Variables(83).ValuesAsNumpy()
        hourly_geopotential_height_600hPa = hourly.Variables(84).ValuesAsNumpy()
        hourly_geopotential_height_950hPa = hourly.Variables(85).ValuesAsNumpy()
        hourly_geopotential_height_850hPa = hourly.Variables(86).ValuesAsNumpy()
        hourly_cloud_cover = hourly.Variables(87).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(88).ValuesAsNumpy()
        hourly_wind_gusts_10m = hourly.Variables(89).ValuesAsNumpy()
        hourly_wind_direction_10m = hourly.Variables(90).ValuesAsNumpy()
        hourly_cape = hourly.Variables(91).ValuesAsNumpy()
        hourly_lifted_index = hourly.Variables(92).ValuesAsNumpy()
        hourly_convective_inhibition = hourly.Variables(93).ValuesAsNumpy()
        hourly_uv_index = hourly.Variables(94).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}

        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["weather_code"] = hourly_weather_code
        hourly_data["precipitation_probability"] = hourly_precipitation_probability
        hourly_data["apparent_temperature"] = hourly_apparent_temperature
        hourly_data["dew_point_2m"] = hourly_dew_point_2m
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["surface_pressure"] = hourly_surface_pressure
        hourly_data["temperature_1000hPa"] = hourly_temperature_1000hPa
        hourly_data["temperature_925hPa"] = hourly_temperature_925hPa
        hourly_data["temperature_800hPa"] = hourly_temperature_800hPa
        hourly_data["temperature_100hPa"] = hourly_temperature_100hPa
        hourly_data["temperature_250hPa"] = hourly_temperature_250hPa
        hourly_data["temperature_500hPa"] = hourly_temperature_500hPa
        hourly_data["temperature_200hPa"] = hourly_temperature_200hPa
        hourly_data["temperature_400hPa"] = hourly_temperature_400hPa
        hourly_data["temperature_700hPa"] = hourly_temperature_700hPa
        hourly_data["temperature_900hPa"] = hourly_temperature_900hPa
        hourly_data["temperature_975hPa"] = hourly_temperature_975hPa
        hourly_data["temperature_150hPa"] = hourly_temperature_150hPa
        hourly_data["temperature_300hPa"] = hourly_temperature_300hPa
        hourly_data["temperature_600hPa"] = hourly_temperature_600hPa
        hourly_data["temperature_850hPa"] = hourly_temperature_850hPa
        hourly_data["temperature_950hPa"] = hourly_temperature_950hPa
        hourly_data["relative_humidity_1000hPa"] = hourly_relative_humidity_1000hPa
        hourly_data["relative_humidity_800hPa"] = hourly_relative_humidity_800hPa
        hourly_data["relative_humidity_925hPa"] = hourly_relative_humidity_925hPa
        hourly_data["relative_humidity_500hPa"] = hourly_relative_humidity_500hPa
        hourly_data["relative_humidity_250hPa"] = hourly_relative_humidity_250hPa
        hourly_data["relative_humidity_100hPa"] = hourly_relative_humidity_100hPa
        hourly_data["relative_humidity_200hPa"] = hourly_relative_humidity_200hPa
        hourly_data["relative_humidity_400hPa"] = hourly_relative_humidity_400hPa
        hourly_data["relative_humidity_700hPa"] = hourly_relative_humidity_700hPa
        hourly_data["relative_humidity_900hPa"] = hourly_relative_humidity_900hPa
        hourly_data["relative_humidity_975hPa"] = hourly_relative_humidity_975hPa
        hourly_data["relative_humidity_150hPa"] = hourly_relative_humidity_150hPa
        hourly_data["relative_humidity_300hPa"] = hourly_relative_humidity_300hPa
        hourly_data["relative_humidity_600hPa"] = hourly_relative_humidity_600hPa
        hourly_data["relative_humidity_850hPa"] = hourly_relative_humidity_850hPa
        hourly_data["relative_humidity_950hPa"] = hourly_relative_humidity_950hPa
        hourly_data["wind_speed_100hPa"] = hourly_wind_speed_100hPa
        hourly_data["wind_speed_250hPa"] = hourly_wind_speed_250hPa
        hourly_data["wind_speed_500hPa"] = hourly_wind_speed_500hPa
        hourly_data["wind_speed_800hPa"] = hourly_wind_speed_800hPa
        hourly_data["wind_speed_1000hPa"] = hourly_wind_speed_1000hPa
        hourly_data["wind_speed_925hPa"] = hourly_wind_speed_925hPa
        hourly_data["wind_speed_200hPa"] = hourly_wind_speed_200hPa
        hourly_data["wind_speed_400hPa"] = hourly_wind_speed_400hPa
        hourly_data["wind_speed_700hPa"] = hourly_wind_speed_700hPa
        hourly_data["wind_speed_900hPa"] = hourly_wind_speed_900hPa
        hourly_data["wind_speed_975hPa"] = hourly_wind_speed_975hPa
        hourly_data["wind_speed_150hPa"] = hourly_wind_speed_150hPa
        hourly_data["wind_speed_300hPa"] = hourly_wind_speed_300hPa
        hourly_data["wind_speed_600hPa"] = hourly_wind_speed_600hPa
        hourly_data["wind_speed_850hPa"] = hourly_wind_speed_850hPa
        hourly_data["wind_speed_950hPa"] = hourly_wind_speed_950hPa
        hourly_data["wind_direction_1000hPa"] = hourly_wind_direction_1000hPa
        hourly_data["wind_direction_925hPa"] = hourly_wind_direction_925hPa
        hourly_data["wind_direction_500hPa"] = hourly_wind_direction_500hPa
        hourly_data["wind_direction_250hPa"] = hourly_wind_direction_250hPa
        hourly_data["wind_direction_100hPa"] = hourly_wind_direction_100hPa
        hourly_data["wind_direction_800hPa"] = hourly_wind_direction_800hPa
        hourly_data["wind_direction_400hPa"] = hourly_wind_direction_400hPa
        hourly_data["wind_direction_200hPa"] = hourly_wind_direction_200hPa
        hourly_data["wind_direction_900hPa"] = hourly_wind_direction_900hPa
        hourly_data["wind_direction_700hPa"] = hourly_wind_direction_700hPa
        hourly_data["wind_direction_975hPa"] = hourly_wind_direction_975hPa
        hourly_data["wind_direction_600hPa"] = hourly_wind_direction_600hPa
        hourly_data["wind_direction_150hPa"] = hourly_wind_direction_150hPa
        hourly_data["wind_direction_300hPa"] = hourly_wind_direction_300hPa
        hourly_data["wind_direction_850hPa"] = hourly_wind_direction_850hPa
        hourly_data["wind_direction_950hPa"] = hourly_wind_direction_950hPa
        hourly_data["geopotential_height_100hPa"] = hourly_geopotential_height_100hPa
        hourly_data["geopotential_height_250hPa"] = hourly_geopotential_height_250hPa
        hourly_data["geopotential_height_500hPa"] = hourly_geopotential_height_500hPa
        hourly_data["geopotential_height_800hPa"] = hourly_geopotential_height_800hPa
        hourly_data["geopotential_height_925hPa"] = hourly_geopotential_height_925hPa
        hourly_data["geopotential_height_1000hPa"] = hourly_geopotential_height_1000hPa
        hourly_data["geopotential_height_200hPa"] = hourly_geopotential_height_200hPa
        hourly_data["geopotential_height_400hPa"] = hourly_geopotential_height_400hPa
        hourly_data["geopotential_height_700hPa"] = hourly_geopotential_height_700hPa
        hourly_data["geopotential_height_900hPa"] = hourly_geopotential_height_900hPa
        hourly_data["geopotential_height_975hPa"] = hourly_geopotential_height_975hPa
        hourly_data["geopotential_height_150hPa"] = hourly_geopotential_height_150hPa
        hourly_data["geopotential_height_300hPa"] = hourly_geopotential_height_300hPa
        hourly_data["geopotential_height_600hPa"] = hourly_geopotential_height_600hPa
        hourly_data["geopotential_height_950hPa"] = hourly_geopotential_height_950hPa
        hourly_data["geopotential_height_850hPa"] = hourly_geopotential_height_850hPa
        hourly_data["cloud_cover"] = hourly_cloud_cover
        hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
        hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m
        hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
        hourly_data["cape"] = hourly_cape
        hourly_data["lifted_index"] = hourly_lifted_index
        hourly_data["convective_inhibition"] = hourly_convective_inhibition
        hourly_data["uv_index"] = hourly_uv_index

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_cape_mean = daily.Variables(0).ValuesAsNumpy()
        daily_cape_max = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
        daily_apparent_temperature_mean = daily.Variables(3).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(4).ValuesAsNumpy()
        daily_sunrise = daily.Variables(5).ValuesInt64AsNumpy()
        daily_sunset = daily.Variables(6).ValuesInt64AsNumpy()
        daily_sunrise = [datetime.fromtimestamp(ts).strftime("%H:%M") for ts in daily_sunrise]
        daily_sunset = [datetime.fromtimestamp(ts).strftime("%H:%M") for ts in daily_sunset]



        daily_precipitation_probability_max = daily.Variables(7).ValuesAsNumpy()
        daily_uv_index_max = daily.Variables(8).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )}

        daily_data["cape_mean"] = daily_cape_mean
        daily_data["cape_max"] = daily_cape_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["apparent_temperature_mean"] = daily_apparent_temperature_mean
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["sunrise"] = daily_sunrise
        daily_data["sunset"] = daily_sunset
        daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
        daily_data["uv_index_max"] = daily_uv_index_max

        print("Beginning elaboration")

        daily_dataframe = pd.DataFrame(data=daily_data)
        #endregion

        pressure_levels = [1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 150, 100]

        srh_pos = []
        srh_neg = []
        srh_tot = []
        bunkers_right = []
        bunkers_left = []
        bunkers_mean = []
        bulkshear06 = []

        cnt = 0
        for index, row in hourly_dataframe.iterrows():

            above_ground_heights = []
            above_ground_u = []
            above_ground_v = []
            above_ground_pressure = []

            for level in pressure_levels:
                height_col = f"geopotential_height_{level}hPa"
                wind_speed_col = f"wind_speed_{level}hPa"
                wind_dir_col = f'wind_direction_{level}hPa'
                if height_col in hourly_dataframe.columns and wind_speed_col in hourly_dataframe.columns and wind_dir_col in hourly_dataframe.columns:
                    height = row[height_col]
                    speed = row[wind_speed_col]
                    direction = row[wind_dir_col]
                    if pd.notna(height) and pd.notna(speed) and pd.notna(direction) and height > elevation:
                        above_ground_pressure.append(level)
                        above_ground_heights.append(height)
                        u_comp, v_comp = wind_components(
                            (speed * (units.kilometer / units.hour)).to(units.meter/ units.second),
                            direction * units.degree)
                        above_ground_u.append(u_comp.magnitude)
                        above_ground_v.append(v_comp.magnitude)
            if len(above_ground_heights) > 2:
                above_ground_heights = above_ground_heights * units.meter
                above_ground_u = above_ground_u * (units.meter / units.second)
                above_ground_v = above_ground_v * (units.meter / units.second)
                above_ground_pressure = above_ground_pressure * units.hPa
                right_mover, left_mover, mean = bunkers_storm_motion(above_ground_pressure, above_ground_u, above_ground_v, above_ground_heights)
                cnt+=1
                to_choose = right_mover if lat > 0 else left_mover

                srh = storm_relative_helicity(above_ground_heights, above_ground_u, above_ground_v, depth=3000*units.meter, bottom=elevation*units.meter
                                              , storm_u=to_choose[0], storm_v=to_choose[1])
                print(mean)
                srh_pos.append(srh[0].magnitude)
                srh_neg.append(srh[1].magnitude)
                srh_tot.append(srh[2].magnitude)

                u_shear, v_shear = bulk_shear(above_ground_pressure, above_ground_u, above_ground_v, above_ground_heights, depth=6000*units.meters)
                bulkshear = ((np.sqrt(u_shear.magnitude**2 + v_shear.magnitude**2))*(units.meter/units.second)).to(units.knot).magnitude
                bulkshear06.append(bulkshear)
                bunkers_right.append(right_mover.to(units.kilometer/units.hour).magnitude)
                bunkers_left.append(left_mover.to(units.kilometer/units.hour).magnitude)
                bunkers_mean.append(mean.to(units.kilometer/units.hour).magnitude)


        print(cnt)
        print(bunkers_mean)
        self.daily = daily_dataframe
        self.minutely = minutely_15_dataframe

        print(self.daily)
        print(self.minutely)
        hourly_dataframe["srh_pos"] = srh_pos
        hourly_dataframe["srh_neg"] = srh_neg
        hourly_dataframe["srh_tot"] = srh_tot
        hourly_dataframe["bulk_shear"] = bulkshear06



        dfs = [daily_dataframe, hourly_dataframe, minutely_15_dataframe]

        return dfs

