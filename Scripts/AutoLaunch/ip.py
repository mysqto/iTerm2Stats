#!/usr/bin/env python3
import asyncio
import json
import socket
import urllib.error
import urllib.request

import iterm2

# The name of the iTerm2 variable to store the result
VARIABLE = "external_ip"
URL = "https://ifconfig.co/json"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1" \
             " Safari/605.1.15"

service_url = None
update_interval = 120

# Icons are base64-encoded PNGs. The first one is 32x34 and is used for Retina
# displays. The second is 16x32 and is used for non-Retina displays.
ICON1X = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA7klEQVQ4jbWRvWpCQRCFP41I/AGfwoi+gNhYqm2w0kdIE6K+xu3FxjdIi" \
         "JU2VlaKXWoLk0K0s1TBsDADA9l7vSk8MHDYPefM7gz3Qhf4BH6kHO/E6ZUX8TWkJqIJxSzCrDUNM7eN6Eue7vhaOm/M/bMv4MMInoCB8C" \
         "zQAErAXM7e1ZQ0AWXDM0BaeAHoAXv5okPFF2D5CbgIPwIv8sW+nCVUmDKmFVA023gUngPGQN1ol74Z1MwMDtLZ8Z1nE1VfgEMQY41BmFk" \
         "xijAPb5kVbzJENTr+GtesaJmA5n/Nim9gGyV4uBFwBhay4r8AfgFM5lUYQdNtmQAAAABJRU5ErkJggg=="

ICON2X = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAABnUlEQVRIieXWu2sVQRTH8c8VX7cwV9OZh" \
         "KRNwETEv0B7NZW1IKQSsQwG/xY7TRHCRUEU/wNFfICojRZaJFgkNqYxXIudhWUzN87s3cQiPziwc+bxPfM6sxw1dTLajmMR1zGLqeD/gU" \
         "94gj622gquixX8wuAfto37oc9ImsCrBGDd3mK6KXRKsYy50NK+YzIX2sWbEaClvcbpHPCDFqClLadCx6UdpFTbxrk65FgEvIixiL8TbKf" \
         "i61X8JzCPZ7V+PdzYf66F+kMiL/W74isDvIObYSJdfKv1XU8Bf2kA3gjla6H8sNb3cx0SW+rzKdFFtKO4QnC2VjeROkDujGdwJnxfiIxR" \
         "PRfgeAS8GQbK0YJilhexZO/d3UgZZF3zPR5ma3VIbI9XU6LL1OOURqfwU3sJZBMnUyO83SL4ViqUIhO9bAH6XN7PBoqD834E6EeRHJ2qS" \
         "XxoAH0nMWnspx6eZkD74o9MI3Vwz/CsNlDc77sa7GmK5ux9eQb4GuoOVJexW4H+waWDhpZarYAfHRYUrlbAVw4T3MELDRPEf9Vfh9wnPh" \
         "AHcssAAAAASUVORK5CYII="

FLAGS_OFFSET = 127397
A = 65
Z = 90


def emoji(country):
    first = ord(country[0])
    second = ord(country[1])

    if (len(country) != 2) or (first > Z or first < A) or (second > Z or second < A):
        return country

    return chr(first + FLAGS_OFFSET) + chr(second + FLAGS_OFFSET)


async def get_external_ip():
    try:
        request = urllib.request.Request(URL, data=None,
                                         headers={
                                             'User-Agent': USER_AGENT
                                         }
                                         )

        with urllib.request.urlopen(request) as response:
            resp = response.read().decode("utf-8").strip()
            obj = json.loads(resp)
            return '{}|{}'.format(obj["ip"], emoji(obj["country_iso"]))
    except (urllib.error.HTTPError, urllib.error.URLError, TypeError):
        return '{}|{}'.format(local_ip(), '📶')


def local_ip():
    return socket.gethostbyname(socket.gethostname())


async def external_ip_task(app):
    while True:
        global update_interval
        text = await get_external_ip()
        if text:
            await app.async_set_variable("user." + VARIABLE, text)
            await asyncio.sleep(update_interval)
        else:
            await asyncio.sleep(5)


async def main(connection):
    app = await iterm2.async_get_app(connection)
    # Start fetching the URL
    asyncio.create_task(external_ip_task(app))

    icon1x = iterm2.StatusBarComponent.Icon(1, ICON1X)
    icon2x = iterm2.StatusBarComponent.Icon(2, ICON2X)

    update_interval_knob = "ip_update_interval"
    knobs = [iterm2.StringKnob("Update Interval", "60", "60", update_interval_knob)]

    # Register the status bar component.
    component = iterm2.StatusBarComponent(
        short_description="External IP",
        detailed_description="Shows public IP address of current host",
        knobs=knobs,
        exemplar=local_ip(),
        update_cadence=None,
        identifier="catj.moe.ip",
        icons=[icon1x, icon2x])

    # This function gets called once per second.
    @iterm2.StatusBarRPC
    async def external_ip(knobs, value=iterm2.Reference("iterm2.user." + VARIABLE + "?")):
        global update_interval
        if update_interval_knob in knobs and knobs[update_interval_knob]:
            update_interval = int(knobs[update_interval_knob])
        """This function returns the value to show in a status bar."""
        if value:
            return value
        return local_ip()

    # Register the component.
    await component.async_register(connection, external_ip)


# This instructs the script to run the "main" coroutine and to keep running even after it returns.
iterm2.run_forever(main)
