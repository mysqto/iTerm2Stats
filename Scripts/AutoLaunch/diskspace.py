#!/usr/bin/env python3

import os

import iterm2

# Icons are base64-encoded PNGs. The first one is 32x34 and is used for Retina
# displays. The second is 16x32 and is used for non-Retina displays.
ICON1X = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA90lEQVQ4ja3RzyrEURQH8M/4Wyg2SiyUhaXEC9h5AltvYMc8iaXyCLZ2G" \
         "sVmosjSgmIrYxSzGk0d03W7/fyUU9/uved87/fe8z3+M5q4RwdP6KIf6EauE5yD0rut5MIAPZwHelmt9ZvAFRaT2lLkagtsFOqbJYGRAr" \
         "GN69jvBcQP2jl5rCAwleyf8ZGcJ+sIrOIUd9hP8jtYy8mlFsaxjbk4N7CL4wL3R+RjrMLQxEYisY4tLOM9+p2N2hs+MYNHnOEm92Aatzj" \
         "BROGH/RBcyIweRp0WHmK9qDKxKg5jtN+tGU3Y81iJtl7ChxyD6bziCJd/fLwQ+AIy61YKYfXMKgAAAABJRU5ErkJggg=="

ICON2X = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAABGUlEQVRIie2WQU7DMBBFH1mxCJtyELpCQZR9Iw4AEiuOBFnAistUvUEPU" \
         "JoeIrCgyNJEihLbsZWxBGq/NJJlz8z3jGdsc4LgHtgDh4lSA2VMUmsF0lZ2NoIzB/FB+egHPFmkgy/gFSiAXMSMK1mbDFvKzJlfeRzPPX" \
         "URjL5hM0LaJW80iV8ibCtN4usI20KTOLforIGVZf4ihDi0qs8tcz8J2m6w40WEbVCqQyN+lhS+AZsR3aeITQ7Q3/E38Cnjd4/dXC4SteJ" \
         "qZSuRu0jVL5Bu5B/AHXAp1X7TuTJddgP8uUdir0haxyiXSm+yeYuXikGkwwMwU/BufDzaFv7ND0QNqYhvpdedSEWceY7Ri+TfWxeOr4/T" \
         "AvgFCTzPXfv9MzgAAAAASUVORK5CYII="


def format_bytes(num, used, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s|%2.2f%%" % (num, unit, suffix, used)
        num /= 1024.0
    return "%.1f %s%s|%2.2f%%" % (num, 'Yi', suffix, used)


def get_free_space(disk='/'):
    statvfs = os.statvfs(disk)
    total = statvfs.f_blocks * statvfs.f_frsize
    free = statvfs.f_frsize * statvfs.f_bavail
    used = ((total - free) / total) * 100.00
    return format_bytes(free, used)


async def main(connection):
    icon1x = iterm2.StatusBarComponent.Icon(1, ICON1X)
    icon2x = iterm2.StatusBarComponent.Icon(2, ICON2X)

    component = iterm2.StatusBarComponent(
        short_description="Free Space",
        detailed_description="Shows the amount of free disk space",
        knobs=[],
        exemplar="💾 " + get_free_space(),
        update_cadence=60,
        identifier="catj.moe.diskspace",
        icons=[icon1x, icon2x])

    # This function gets called once per second.
    @iterm2.StatusBarRPC
    async def diskspace(knobs):
        return str(get_free_space())

    # Register the component.
    await component.async_register(connection, diskspace)


# This instructs the script to run the "main" coroutine and to keep running even after it returns.
iterm2.run_forever(main)
