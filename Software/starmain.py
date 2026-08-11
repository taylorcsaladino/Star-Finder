
"""
Master file. Run this.
 
Flow: connect -> home -> calibrate (2 objects) -> target menu.
Live tracking is not wired yet (deferred).
 
Requires: pyserial, skyfield   ->   pip install pyserial skyfield
"""
 
from mount import Mount
from Starmenu import Sky, menu
from Calibration_n_home import home, calibration
 
 
def main():
    # 1. connect to the Arduino
    port = input("Arduino serial port (e.g. COM3): ").strip()
    mount = Mount(port)
 
    # the try/finally guarantees the serial port is released even if a later
    # step crashes or you Ctrl-C out of an input() -- otherwise COM stays held
    # and the next run fails with 'Access is denied'.
    try:
        # 2. observer location
        lat = float(input("Latitude  (+N / -S): "))
        lon = float(input("Longitude (+E / -W): "))
        print("Loading ephemeris + star catalog...")
        sky = Sky(lat, lon)
 
        # 3. home, then calibrate
        home(mount)
        offset = calibration(mount, sky)
 
        # 4. point at things
        menu(mount, sky, offset)
    finally:
        mount.close()
 
 
if __name__ == "__main__":
    main()
