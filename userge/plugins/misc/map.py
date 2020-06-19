#Copyright (C) 2020 rzlamrr
#
#Original module from @skittles9823 < https://github.com/skittles9823/SkittBot >
#Ported to UsergeX by @rzlamrr < https://github.com/rzlamrr/UsergeX >

import requests
from userge import userge, Message

from geopy.geocoders import Nominatim


@userge.on_cmd("map", about={
    'header': "Get map of a location",
    'usage': "{tr}map [location]",
    'examples': "{tr}map Jakarta"})
async def map(message: Message) -> None:
    text = message.input_or_reply_str
    await message.edit("Using God Eye...")
    try:
        geolocator = Nominatim(user_agent="SkittBot")
        location = text
        geoloc = geolocator.geocode(location)  
        lon = geoloc.longitude
        lat = geoloc.latitude
        await message.delete()
        await userge.send_location(message.chat.id, lon, lat)
        output = f"Open {text} with [Google Maps](https://www.google.com/maps/search/{lat},{lon})"
        await userge.send_message(message.chat.id, output, disable_web_page_preview=True)
    except AttributeError:
        await message.edit(f"Can't find {text}", del_in=10)
