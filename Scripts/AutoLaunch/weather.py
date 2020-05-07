#!/usr/bin/env python3

import asyncio
import urllib.request

import iterm2

# The URL to request
CURRENT_URL = 'https://wttr.in/{}?m&format=%c+%t+%w+%h'
FORECAST_URL = 'https://wttr.in/{}?3&A&F&n&T&Q'

# The name of the iTerm2 variable to store the result
CURRENT_VARIABLE = "current_weather"
FORECAST_VARIABLE = "forecast_weather"
CITY_VARIABLE = "user.weather_city"
UPDATE_VARIABLE_VARIABLE = "user.weather_update_interval"

city = None
update_interval = 60

# Icons are base64-encoded PNGs. The first one is 32x34 and is used for Retina
# displays. The second is 16x32 and is used for non-Retina displays.
ICON1X = "iVBORw0KGgoAAAANSUhEUgAAABAAAAARCAYAAADUryzEAAAABGdBTUEAALGPC/xhBQAAAK9JREFUOMtjYKAxqIRiskE9FBMFvIDYEYgZo" \
         "XxJIDaHYkmoGEjOCYg9sRnABMQWQKwDxLuA+BoQz4Ti61AxkEZ+qFqsgAuIbwNxGZoiJqjYbaganKANiOfikZ8LVYMTnAFiYzzyxlA1GF" \
         "H1GYnmwWMAD5pacBSzQiVYSXABsh7qhgHFsaAExHZ40gFIThGX5iAg1gBiZmiKk4T62RgpJYLkYoBYd3BmJmyAFVtUIQMAZuAlWgiKRrs" \
         "AAAAASUVORK5CYII="

ICON2X = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAiCAYAAAA+stv/AAAABGdBTUEAALGPC/xhBQAAAWJJREFUWMPtVzsOgkAQRRIas4UdsTI0FhzDG" \
         "1BwChrOYW1nTaPewsIL2JDY2HgBKisdk0cyEl2XWcniZ5KXEJiZ99hdZgbP+5udnQBndgG+T8CAMHyjgCFyGpMvCVuCeuE7BnSmkGtpKi" \
         "IkHPFmTREBISUUhJJQASXupfBpkl+QMzRdhYiJWOFeQjiwZX+GA3w9xNbkUdtzcAvYEaaEOSPYE3JCjDdUuM7xrPabI3YnIedWk58JGcH" \
         "X+PrwOTMRVpYw8lmLuBkTkUjJA7bnmSA+Y2cikAhI2Z77gnifnYlUIqBAcG6xhTlyFJLgEsGxhYAYOUrTrsa7W4VgZSFAIUel4bmr6by2" \
         "dyHgEc9dTee1vYsteMTT30Po/DN0Xoicl2Lnzej2CS0II4t2PEIOJSGvJ5m1xUCyeTJZGZM3J5m2I1mkGe9eChCNUZrxrvUqTN74ZzSxL" \
         "Ok/+Gf0MQKMulqv7Qpwm6+awd/XXAAAAABJRU5ErkJggg=="


async def get_weather(url, location=None):
    try:
        req = urllib.request.Request(
            url.format(location),
            data=None,
            headers={
                'User-Agent': 'curl/7.64.1'
            }
        )
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except (urllib.error.HTTPError, urllib.error.URLError, TypeError):
        return None


async def updater(app, type='current'):
    """A background tasks that reloads URL every UPDATE_INTERVAL seconds and
    sets the app-scope 'user.{WEATHER_VARIABLE}' variable."""
    while True:
        global city
        global update_interval

        if not city:
            await asyncio.sleep(1)
            continue

        weather_url = CURRENT_URL
        variable_key = CURRENT_VARIABLE

        if type == 'forecast':
            weather_url = FORECAST_URL
            variable_key = FORECAST_VARIABLE

        weather = await get_weather(weather_url, city)
        print(weather)

        if weather:
            if type == 'current':
                weather = weather.strip()
            await app.async_set_variable("user." + variable_key, weather)
            await asyncio.sleep(update_interval)
        else:
            await asyncio.sleep(1)

async def format_weather(app):
    text = await app.async_get_variable("user." + FORECAST_VARIABLE)
    style = "<style>pre {font-family: Menlo,monospace; font-size: 12}</style>"
    return style + '<pre>' + text + '</pre>' if text is not None else None

async def main(connection):
    app = await iterm2.async_get_app(connection)
    # Start fetching the URL
    asyncio.create_task(updater(app, type='current'))
    asyncio.create_task(updater(app, type='forecast'))

    location_knob = "weather_location"
    update_interval_knob = "weather_update_interval"
    knobs = [iterm2.StringKnob("Location", "Hangzhou", "Hangzhou", location_knob),
             iterm2.StringKnob("Update Interval", "60", "60", update_interval_knob)]

    # icon1x = iterm2.StatusBarComponent.Icon(1, ICON1X)
    # icon2x = iterm2.StatusBarComponent.Icon(2, ICON2X)

    # Register the status bar component.
    component = iterm2.StatusBarComponent(
        short_description="Weather",
        detailed_description="Shows your local weather",
        knobs=knobs,
        exemplar="☁️Weather",
        update_cadence=None,
        identifier="catj.moe.weather")

    @iterm2.StatusBarRPC
    async def weather(knobs, value=iterm2.Reference("iterm2.user." + CURRENT_VARIABLE + "?")):
        """This function returns the value to show in a status bar."""
        global city
        global update_interval
        if location_knob in knobs and knobs[location_knob]:
            city = knobs[location_knob]
        if update_interval_knob in knobs and knobs[update_interval_knob]:
            update_interval = int(knobs[update_interval_knob])

        if value:
            return value
        return "Loading…"

    @iterm2.RPC
    async def onclick(session_id):
        session = app.get_session_by_id(session_id)
        forecast_weather = await format_weather(app)
        if forecast_weather is not None:
            await component.async_open_popover(session_id, forecast_weather, iterm2.util.Size(480, 520))

    # Register the component.
    await component.async_register(connection, weather, onclick=onclick)


iterm2.run_forever(main)
