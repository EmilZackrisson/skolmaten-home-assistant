"""Feedparser sensor"""
from __future__ import annotations

import asyncio
import re
from datetime import timedelta,datetime

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from dateutil import parser
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


from bs4 import BeautifulSoup
import requests, json, sys


__version__ = "1.0.0"

COMPONENT_REPO = "https://github.com/EmilZackrisson/home-assistant-skolmaten"

CONF_SCHOOL = "school"
CONF_SPLIT_ALTERNATIVE = "split_alternative_course"

DEFAULT_SCAN_INTERVAL = timedelta(hours=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_SCHOOL): cv.string,
        vol.Required(CONF_SPLIT_ALTERNATIVE): cv.bool
    }
)


@asyncio.coroutine
def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_devices: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    async_add_devices(
        [
            SkolmatenSensor(
                school=config[CONF_SCHOOL],
                name=config[CONF_NAME],
                splitAlt=config[CONF_SPLIT_ALTERNATIVE],
            )
        ],
        True,
    )


class SkolmatenSensor(SensorEntity):
    def __init__(
        self,
        school: str,
        name: str,
        splitAlt: bool,
    ) -> None:
        self._school = school
        self._attr_name = name
        self._attr_icon = "mdi:food"
        self._attr_state = None
        self._entries = []
        self._attr_extra_state_attributes = {"entries": self._entries}

    def update(self):
        feed = 'https://skolmaten.se/' + self._school + '/rss/weeks/?offset=0'

        SkolmatenSensor.page = requests.get('https://skolmaten.se/' + self._school + '/rss/weeks/?offset=0')
        self._result         = BeautifulSoup(SkolmatenSensor.page.content, "html.parser")
        self._attributes     = {}
        school = []
        for item in self._result.select('item'):
            day        = item.select('title')[0].text.strip()
            food       = item.select('description')[0].text.strip()
            date       = item.select('pubDate')[0].text
            parsedDate = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
            if "todaysFood" not in vars():
                todaysFood = "no food found for today"

            if parsedDate.date() == datetime.today().date():
                todaysFood = food

            school.append({
                'day' : day,
                'date': date,
                'food': food
            });
        self._state = sys.getsizeof(school)
        if "todaysFood" in vars():
            self._attributes.update({"todaysFood": todaysFood})
        self._attributes.update({"entries": school})

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._attr_state

    @property
    def extra_state_attributes(self):
        return {"entries": self._entries}