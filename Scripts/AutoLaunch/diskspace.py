#!/usr/bin/env python3

import os
import psutil
from psutil._common import bytes2human
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


def get_free_space(disk='/'):
    statvfs = os.statvfs(disk)
    total = statvfs.f_blocks * statvfs.f_frsize
    free = statvfs.f_frsize * statvfs.f_bavail
    used = ((total - free) / total) * 100.00
    return "{:>5}|{:.2f}%".format(bytes2human(free), used)

def df():
    disk_usage = '<style>td    {padding: 6px;}</style>'
    disk_usage += '<table>'
    table_headers = ["Device", "Total", "Used", "Free", "Use ", "Type", "Mount"]

    disk_usage += '  <tr>'
    for head in table_headers:
        disk_usage += '    <th>{}</th>'.format(head)
    disk_usage += '  </tr>'

    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                # skip cd-rom drives with no disk in it; they may raise
                # ENOENT, pop-up a Windows GUI error for a non-ready
                # partition or just hang.
                continue

        usage = psutil.disk_usage(part.mountpoint)
        disk_usage += '  <tr>'
        disk_usage += '    <td>{}</td>'.format(part.device)
        disk_usage += '    <td>{}</td>'.format(bytes2human(usage.total))
        disk_usage += '    <td>{}</td>'.format(bytes2human(usage.used))
        disk_usage += '    <td>{}</td>'.format(bytes2human(usage.free))
        disk_usage += '    <td>{:.2f}%</td>'.format(usage.percent)
        disk_usage += '    <td>{}</td>'.format(part.fstype)
        disk_usage += '    <td>{}</td>'.format(part.mountpoint)
        disk_usage += '  </tr>'

    disk_usage += '</table>'

    return disk_usage



    templ = "%-17s %8s %8s %8s %5s%% %9s  %s\n"
    disk_usage += templ % ("Device", "Total", "Used", "Free", "Use ", "Type",
                   "Mount")
    for part in psutil.disk_partitions(all=False):
        usage = psutil.disk_usage(part.mountpoint)
        disk_usage += templ % (
            part.device,
            bytes2human(usage.total),
            bytes2human(usage.used),
            bytes2human(usage.free),
            int(usage.percent),
            part.fstype,
            part.mountpoint)
    return disk_usage


async def main(connection):
    app = await iterm2.async_get_app(connection)
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

    @iterm2.RPC
    async def onclick(session_id):
        session = app.get_session_by_id(session_id)
        await component.async_open_popover(session_id, df(), iterm2.util.Size(660, 320))

    # Register the component.
    await component.async_register(connection, diskspace, onclick=onclick)


# This instructs the script to run the "main" coroutine and to keep running even after it returns.
iterm2.run_forever(main)
