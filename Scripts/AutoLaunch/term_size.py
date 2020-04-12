#!/usr/bin/env python3

import iterm2

# Icons are base64-encoded PNGs. The first one is 32x34 and is used for Retina
# displays. The second is 16x32 and is used for non-Retina displays.

ICON1X = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA2klEQVQ4jcXSvUpDQRQE4C+SVMEfRBRTBMRKRLSxSWuVTvBtfAsfxEdIH" \
         "bCQQJJeBEWwSGGrKBvOhWUluUYQB5bl7DnMzsyuf0cjE3CLixUEDXCVE3z+wk2jmRVvGMVeh3WclTMz7P/w5r2Yt1Y0NtCOfRl2ql5J8I" \
         "pDPOF8mfdFBLsY4wZ36NV5KQla8RrTqLfqFORIoWzjJEguozfES7a6kcE8xGZB8oEJDvAQZ9dFqI/YrIqcIMnt4z7Yk5IkNf2N92zuCKe" \
         "VvdxL8t1ZHNc3PON4hfm/AL4A1iEgxfWGgUIAAAAASUVORK5CYII="

ICON2X = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAAAwUlEQVRIie2WsQ6CMBBAn8Zf0Oj3OBn/W" \
         "pxEFxncxclvMMHBlpBCbbU9aYSXdDku9+j1SIGRobEFbkAVeZXA5p24FJDqdW2KJoa48uhKCLVvKiyy0pt4ZombRxBK6wiH1+qkxTvgCC" \
         "wkX0R/7E0OKlYEyLvqOhPmwFnFL8DqV2J47bRQz/IY4t6Gy8Sn1ctIdZ0JOd3DlWG/iTJXXZ9WP4ATsAbuHvla9BHOlnxJOsOV3LUo/Sf" \
         "S2vFe0GVO+sif8wRYPGVgAs4YsAAAAABJRU5ErkJggg=="


async def main(connection):
    icon1x = iterm2.StatusBarComponent.Icon(1, ICON1X)
    icon2x = iterm2.StatusBarComponent.Icon(2, ICON2X)
    component = iterm2.StatusBarComponent(
        short_description="Term size",
        detailed_description="Display current terminal size in columns x rows",
        knobs=[],
        exemplar="80x24",
        update_cadence=None,
        identifier="catj.moe.term.size",
        icons=[icon1x, icon2x])

    @iterm2.StatusBarRPC
    async def term_size(knobs,
                        rows=iterm2.Reference("rows"),
                        columns=iterm2.Reference("columns")):
        return "{}x{}".format(columns, rows)

    # Register the component.
    await component.async_register(connection, term_size)


iterm2.run_forever(main)
