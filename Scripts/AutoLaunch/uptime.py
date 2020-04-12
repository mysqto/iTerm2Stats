#!/usr/bin/env python3

import re
import subprocess
import time

import iterm2

# Icons are base64-encoded PNGs. The first one is 32x34 and is used for Retina
# displays. The second is 16x32 and is used for non-Retina displays.
ICON1X = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA4klEQVQ4jdXSsUpDQRAF0BOFRCI2NpJasDSFrdjb+AGKjT+g/oKVja2tR" \
         "cr8gWilINiksFBCbAQb0UoEFVF5MIElbJ7hdV4Ydnf2DvfO7vg3mMMFHrBcxfQsfiJ204vpMQUz2MYSFuM8wCMO8VGmVpD7ieIwWjnyVC" \
         "bXwyvquErya5P0WmAn1tVEvYNNPOMMJ0Ny7g16sZ5jHi/YwD0W8I0nnP7l5CjUb8tIow4aaKOLY7xjHV8xB6W4xGfS90qQ7/A2rrCW7Lf" \
         "QDPJ1/HuBA+zHNFbCXjjKIjcHo7iZpP9qwC8MbTANfstalwAAAABJRU5ErkJggg=="

ICON2X = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAABQ0lEQVRIie3WTysEYRwH8E8iLpTCgUKKG" \
         "xeUiysvwUtQXoG8AW+CF+HI7gGLFBHWWTlwQWIvlNbBbI3dx581M1tbvvUcZn7PPJ+Z53lmGv7ThBlCHiXkMNgoOI9yrG01Cn6ugp++69" \
         "ySInz4w3FmGfIxvc/YlNIa9+HY56mstBcZbaY+XHyBZraZ4mgR81jCaQAupQlXprcY3QT04iEAb0f11jTgAo5iKKwH0DfMYBiXGE8Dj2c" \
         "mQqrhtai+EaiVowdIlJ3AoPfoiepzOA/02U0KlwKDLiYd9DfJqX3atizBAXRgBDdV+HJWaCfOfHwG2zGG2xj8iuk0oG5MYQErOFC7eydw" \
         "Fzt/khTdF34dyrjCaKzvJB5j9UQpfIEeoT/Qf/WvcPXnbbbO66/rBStJ+iPQfHDSdElpjevNE/b+Av+nYXkHMamMFtu4zVEAAAAASUVOR" \
         "K5CYII="


def get_uptime():
    p = subprocess.Popen('sysctl kern.boottime', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)

    for line in p.stdout.readlines():
        boot_time = line.decode("utf-8")
        break

    regex = re.compile('\d+')
    boot_time = regex.findall(boot_time)[0]
    system_uptime = int(time.time()) - int(boot_time)

    days = system_uptime // (24 * 3600)
    system_uptime = system_uptime % (24 * 3600)
    hours = system_uptime // 3600
    system_uptime %= 3600
    minutes = system_uptime // 60
    system_uptime %= 60
    seconds = system_uptime
    days_text = "days" if days > 1 else "day"

    if days > 0:
        return '%d %s %02d:%02d:%02d' % (days, days_text, hours, minutes, seconds)
    else:
        return '%02d:%02d:%02d' % (hours, minutes, seconds)


async def main(connection):
    icon1x = iterm2.StatusBarComponent.Icon(1, ICON1X)
    icon2x = iterm2.StatusBarComponent.Icon(2, ICON2X)

    component = iterm2.StatusBarComponent(
        short_description="Uptime",
        detailed_description="Shows the system uptime since boot",
        knobs=[],
        exemplar='🏃' + get_uptime(),
        update_cadence=1,
        identifier="catj.moe.uptime",
        icons=[icon1x, icon2x])

    # This function gets called once per second.
    @iterm2.StatusBarRPC
    async def uptime(knobs):
        return get_uptime()

    # Register the component.
    await component.async_register(connection, uptime)


iterm2.run_forever(main)
