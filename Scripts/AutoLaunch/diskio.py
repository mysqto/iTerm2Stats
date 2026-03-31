#!/usr/bin/env python3

import asyncio

import iterm2
import psutil
import subprocess
import shutil
import html

last_read = None
last_write = None

# The name of the iTerm2 variable to store the result
DISK_IO_VARIABLE = "disk_io"

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
        return "↑ 0B/s ↓ 0B/s"
    else:
        read_speed = (read - last_read) / interval
        write_speed = (write - last_write) / interval
        last_read = read
        last_write = write
        return "↑ {:<9} ↓ {:<9}".format(readable_bytes(read_speed), readable_bytes(write_speed))


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
        exemplar="↑ 1.2MB/s ↓ 10.5MB/",
        update_cadence=None,
        identifier="catj.moe.disk_io",
        icons=[icon1x, icon2x])

    @iterm2.StatusBarRPC
    async def disk_io_coroutine(knobs, value=iterm2.Reference("iterm2.user." + DISK_IO_VARIABLE + "?")):
        """This function returns the value to show in a status bar."""
        if value:
            return value
        return "Loading…"

    # Helper to collect disk info and format as HTML
    def collect_smart_html():
        out = []
        try:
            diskutil_out = subprocess.check_output(["/usr/sbin/diskutil", "list"], stderr=subprocess.DEVNULL, text=True)
        except Exception:
            diskutil_out = ""

        # Find device names like /dev/disk0, /dev/disk1
        import re
        devices = re.findall(r"(/dev/disk\d+)", diskutil_out)
        # Deduplicate while preserving order
        seen = set()
        devices = [d for d in devices if not (d in seen or seen.add(d))]

        if not devices:
            out.append("No physical disks found (diskutil returned none).")
            combined = "\n\n".join(out)
            return html.escape(combined)

        # Filter to only show physical disks (disk0, disk1, etc. - not disk0sX partitions)
        physical_disks = [d for d in devices if re.match(r'/dev/disk\d+$', d)]
        
        for dev in physical_disks:
            out.append(f"=== {dev} ===\n")
            
            # Use diskutil info which doesn't require root
            try:
                info_out = subprocess.check_output(["/usr/sbin/diskutil", "info", dev], 
                                                   stderr=subprocess.DEVNULL, text=True, timeout=5)
                
                # Parse useful fields from diskutil info
                lines = info_out.split('\n')
                useful_fields = [
                    'Device Identifier:',
                    'Device Node:',
                    'Media Name:',
                    'Protocol:',
                    'SMART Status:',
                    'Disk Size:',
                    'Device Block Size:',
                    'Medium Type:',
                    'Solid State:',
                    'Read-Only Media:',
                    'Removable Media:',
                    'Virtual:'
                ]
                
                filtered_lines = []
                for line in lines:
                    if any(line.strip().startswith(field) for field in useful_fields):
                        filtered_lines.append(line.strip())
                
                if filtered_lines:
                    out.append('\n'.join(filtered_lines))
                else:
                    out.append(info_out)
                    
            except subprocess.TimeoutExpired:
                out.append("Timeout getting disk info")
            except Exception as e:
                out.append(f"Error getting disk info: {e}")
            
            # Try smartctl if available (will likely fail without sudo, but try anyway)
            smartctl_path = shutil.which("smartctl")
            if smartctl_path:
                try:
                    proc = subprocess.run([smartctl_path, "-H", dev], 
                                        capture_output=True, text=True, timeout=3)
                    if proc.returncode == 0 and "PASSED" in proc.stdout:
                        out.append("\nSMART Health: PASSED")
                    elif proc.returncode == 0:
                        out.append(f"\nSMART Status:\n{proc.stdout.strip()}")
                except Exception:
                    pass  # Silently ignore smartctl errors
            
            out.append("")  # Empty line between disks

        # Join results and escape for HTML
        combined = "\n".join(out)
        return html.escape(combined)

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

        smart_html = collect_smart_html()

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
                    overflow: auto !important;
                    font-family: monospace;
                }}
                pre {{
                    white-space: pre-wrap;
                    word-break: break-word;
                    background-color: transparent !important;
                    color: {text_color_css} !important;
                    margin: 0;
                    padding: 6px 8px;
                    border-radius: 6px;
                }}
                h3 {{
                    margin: 8px 0 4px 0;
                    padding: 0;
                    color: {text_color_css} !important;
                }}
                .container {{
                    width: 100%;
                    box-sizing: border-box;
                }}
            </style>
        </head>
        <body style="background-color: {bg_color_css}; color: {text_color_css}; border-radius: 8px; margin: 0; padding: 10px;">
            <div class="container">
                <h2 style="margin:0 0 8px 0;">Disk SMART & Info</h2>
                <pre>{smart_html}</pre>
            </div>
        </body>
        </html>
        """

        # Slightly larger size to account for padding
        await component.async_open_popover(session_id, html_content, iterm2.util.Size(820, 640))

    # Register the component with the onclick handler.
    await component.async_register(connection, disk_io_coroutine, onclick=onclick)


iterm2.run_forever(main)
