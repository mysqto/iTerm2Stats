#!/usr/bin/env python3

import asyncio

import iterm2
import psutil

last_read = None
last_write = None

# The name of the iTerm2 variable to store the result
DISK_IO_VARIABLE = "disk_io"

# Icons are base64-encoded PNGs. The first one is 32x34 and is used for Retina
# displays. The second is 16x32 and is used for non-Retina displays.
ICON1X = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAtUlEQVQ4je3TO2pCURAG4O9qRBANpHEvLiKLcC26C4sswKRJnzaNvTtIF" \
         "fTqbURQDAfmglxOEGIKC38YOPM4/zyY8d94wwkVthmpwv/6W94yAi5JWX9oXdvBneAWCB4a+hjPZwvTRIFHvNf2ohEwwg4b9LGPKjv4Dt" \
         "sAPXzmCNKGddGONU6BhyAaBnlC0p9yMzhiii+8YIEPzMK/xCTiskhHknpP2VdR0Tre9YEl//zvYz8HfgCRWjSaK3yHegAAAABJRU5ErkJ" \
         "ggg=="

ICON2X = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAAAhUlEQVRIie2WQQqAIBAAJ5/Qd6J70QPq/" \
         "eo/7BAdKkWl9RDtwB52FWcRxAXlYAE8EF6GA+YasROQnmFjgi4hDjVdFvDwGGFBMSpWsYpVrOLvir2gw9VsnpH5ky0wibTfmhXoBc7pgS" \
         "22oBPInQEYK/JcvVhsuF5TLs/VszQfb1P87x03Zwfxo2ToywRfigAAAABJRU5ErkJggg=="

# borrow from psutil iostats
def readable_bytes(n, format="%(value).1f%(symbol)s"):
    symbols = ('B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s', 'PB/s', 'EB/s', 'ZB/s', 'YB/s')
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i + 1) * 10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=n)


async def get_disk_io(interval):
    global last_read
    global last_write

    io = psutil.disk_io_counters()
    read = io.read_bytes
    write = io.write_bytes
    if last_read is None or last_write is None:
        last_read = read
        last_write = write
        return "🆁0B/s 🆆️0B/s"
    else:
        read_speed = (read - last_read) / interval
        write_speed = (write - last_write) / interval
        last_read = read
        last_write = write
        return "🆁️{:<9} 🆆️{:<9}".format(readable_bytes(read_speed), readable_bytes(write_speed))


async def poll(app):
    """A background tasks that reloads URL every UPDATE_INTERVAL seconds and
    sets the app-scope 'user.{DISK_IO_VARIABLE}' variable."""
    while True:
        disk_io = await get_disk_io(1)
        
        if disk_io:
            await app.async_set_variable("user." + DISK_IO_VARIABLE, disk_io)
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)


async def main(connection):
    app = await iterm2.async_get_app(connection)
    asyncio.create_task(poll(app))

    icon1x = iterm2.StatusBarComponent.Icon(1, ICON1X)
    icon2x = iterm2.StatusBarComponent.Icon(2, ICON2X)

    # Register the status bar component.
    component = iterm2.StatusBarComponent(
        short_description="Disk IO",
        detailed_description="Shows your overall disk read/write speed",
        knobs=[],
        exemplar="🆁1.2MB/s 🆆️10.5MB/",
        update_cadence=None,
        identifier="catj.moe.disk_io",
        icons=[icon1x, icon2x])

    @iterm2.StatusBarRPC
    async def disk_io_coroutine(knobs, value=iterm2.Reference("iterm2.user." + DISK_IO_VARIABLE + "?")):
        """This function returns the value to show in a status bar."""
        if value:
            return value
        return "Loading…"

    # Register the component.
    await component.async_register(connection, disk_io_coroutine)


iterm2.run_forever(main)
