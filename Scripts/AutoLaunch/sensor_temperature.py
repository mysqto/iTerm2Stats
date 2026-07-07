#!/usr/bin/env python3

import os
import subprocess
from shutil import which

import iterm2

# Icons are base64-encoded PNGs. The first one is 32x34 and is used for Retina
# displays. The second is 16x32 and is used for non-Retina displays.
ICON1X = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABDklEQVQ4jbXTTyuEURQG8B8WxMYws7D0QWjmK1j5MHZW1ixZSnwJWyXb2" \
         "U1IGVGKGklE5+28es3wzmw8dXtu957n3HPPH/+BdeyihX0sJrfyfG3cmzNo5H5piBt5/42pIfEWNrGMFzxiAYPkOJvFCbarwg7m8IBPXC" \
         "b/tW7TvjOdDjYwjw/0sYqjmm/20z50BVbybz28ZYj9mgi6aR+6Agf577MxoZfrHM3UFWimx+6EDsoImmUOdrLegwn76jlLGrofOaiLIDJ" \
         "/nDnqDedgL5vmosbBYdqGo7vMWegKtLOudZmPdZV8n/btsi3j4j1rGz1/gydcV/g1RbGP2ThN3QiqsxBhVnlkFn7D5NOIL7z3a2C90zxb" \
         "AAAAAElFTkSuQmCC"

ICON2X = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAAAuklEQVRIie2X0Q2CMBRFj37jXhJ3YQAdw" \
         "5GMi1BW8Ff9sCVESrH0qjX2JA1pgJzS29cUyJgzcEroe1m/IL4Ct4R+IcgO6HhMWUozQB0jNgKpa61PsJoQqxfHyONWdagE9kAFHAQD6D" \
         "1OHCqBI3Cx11RmS22Y0fCLl+Y8IuuMlURlrKT3fH2qP07J2PFzGUdvr88ZL92hKvv+Bv/O9baMGytvJu7nm3EnlJqYh2s0p5AW2EqG/xe" \
         "UPwkJd/OEn3baB7VUAAAAAElFTkSuQmCC"


def tool_installed(cmd, path=os.environ['PATH']):
    return which(cmd, path=path) is not None

last_smc_temp = None

def get_sensor_temperature():
    env = os.environ.copy()
    pathes = ['/opt/homebrew/bin', '/usr/local/bin']
    for bin_path in pathes:
        if os.path.isdir(bin_path):
            # prepend to PATH
            env["PATH"] = bin_path + ":" + env["PATH"]

    cmd="smctemp"

    if not tool_installed(cmd, env["PATH"]):
        tap = "narugit/tap"
        return f"{cmd} not installed, run brew tap {tap} && brew trust --tap {tap} && brew install {cmd}"
    
    global last_smc_temp
    full_cmd = f"{cmd} -i25 -n10 -f -c"

    try:
        p = subprocess.Popen(full_cmd, shell=True, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

        for line in p.stdout.readlines():
            smc_temp = line.decode("utf-8").strip()
            break
        smc_temp +='°C'
        last_smc_temp = smc_temp
    except Exception as e:
        if last_smc_temp is not None:
            return last_smc_temp
        smc_temp = f"N/A"
    return smc_temp


async def main(connection):
    icon1x = iterm2.StatusBarComponent.Icon(1, ICON1X)
    icon2x = iterm2.StatusBarComponent.Icon(2, ICON2X)

    component = iterm2.StatusBarComponent(
        short_description="Sensor Temperature",
        detailed_description="Shows the sensor(CPU) temperature",
        knobs=[],
        exemplar='🌡️' + get_sensor_temperature(),
        update_cadence=1,
        identifier="catj.moe.sensor.temperature",
        icons=[icon1x, icon2x])

    # This function gets called once per second.
    @iterm2.StatusBarRPC
    async def temperature(knobs):
        return get_sensor_temperature()

    # Register the component.
    await component.async_register(connection, temperature)


iterm2.run_forever(main)
