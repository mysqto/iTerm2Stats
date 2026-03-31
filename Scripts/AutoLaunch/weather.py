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
        try:
            weather = await get_weather(weather_url, city)
        except:
            await asyncio.sleep(1)

        if weather:
            if type == 'current':
                weather = weather.strip()
            await app.async_set_variable("user." + variable_key, weather)
            await asyncio.sleep(update_interval)
        else:
            await asyncio.sleep(5)


async def format_weather(app, bg_color_css, text_color_css):
    text = ""
    try:
        text = await app.async_get_variable("user." + FORECAST_VARIABLE)
    except:
        text = "Loading"
    
    style = f"""
    <style>
        pre {{
            font-family: Menlo,monospace; 
            font-size: 12px;
            color: {text_color_css} !important;
            background-color: {bg_color_css} !important;
            margin: 0;
            padding: 0;
            white-space: pre-wrap;
        }}
    </style>
    """
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
        
        # Get the session's profile to access background color
        profile = await session.async_get_profile()
        background_color = profile.background_color
        
        # Convert background color to CSS format
        bg_color_css = f"rgba({int(background_color.red)}, {int(background_color.green)}, {int(background_color.blue)}, {background_color.alpha})"
        
        # Calculate opposite text color (simple inversion)
        text_red = 255 - int(background_color.red)
        text_green = 255 - int(background_color.green)
        text_blue = 255 - int(background_color.blue)
        text_color_css = f"rgb({text_red}, {text_green}, {text_blue})"

        print(f"Weather - Background color CSS: {bg_color_css}")
        print(f"Weather - Text color CSS: {text_color_css}")
        
        forecast_weather = "Loading"
        try:
            forecast_weather_content = await format_weather(app, bg_color_css, text_color_css)
        except:
            forecast_weather_content = "Loading"
            
        if forecast_weather_content is not None:
            # Create HTML content with matching background color and styling
            html_content = f"""
            <html style="margin: 0; padding: 0; background-color: {bg_color_css}; width: 100%; height: 100%; border-radius: 8px; overflow: hidden;">
            <head>
                <style>
                    html, body {{
                        margin: 0 !important;
                        padding: 10px !important;
                        background-color: {bg_color_css} !important;
                        color: {text_color_css} !important;
                        border: none !important;
                        outline: none !important;
                        width: 100% !important;
                        height: 100% !important;
                        border-radius: 8px !important;
                        overflow: hidden !important;
                        font-family: monospace;
                    }}
                    * {{
                        box-sizing: border-box !important;
                        color: {text_color_css} !important;
                    }}
                </style>
            </head>
            <body style="background-color: {bg_color_css}; color: {text_color_css}; border-radius: 8px; margin: 0; padding: 10px;">
                {forecast_weather_content}
            </body>
            </html>
            """
            await component.async_open_popover(session_id, html_content, iterm2.util.Size(500, 540))

    # Register the component.
    await component.async_register(connection, weather, onclick=onclick)


iterm2.run_forever(main)
