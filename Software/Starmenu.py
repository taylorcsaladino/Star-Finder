"""
Sky (astronomy) + the target-selection menu.
 
Sky resolves any catalog name to (az, alt): planets/Sun/Moon from the ephemeris,
major stars from the Hipparcos catalog. menu() drives pointing after calibration.
Takes a live Mount (mount.py).
"""
 
from skyfield.api import load, wgs84, Star
from skyfield.data import hipparcos
 
 
# --- catalog -------------------------------------------------------------
# Planets + Sun/Moon: resolved by name from the ephemeris file.
PLANETS = {
    "Sun":     "sun",
    "Moon":    "moon",
    "Mercury": "mercury",
    "Venus":   "venus",
    "Mars":    "mars",
    "Jupiter": "jupiter barycenter",
    "Saturn":  "saturn barycenter",
    "Uranus":  "uranus barycenter",
    "Neptune": "neptune barycenter",
}
 
# Major stars: resolved by Hipparcos catalog number.
STARS = {
    "Sirius":     32349,
    "Canopus":    30438,
    "Arcturus":   69673,
    "Vega":       91262,
    "Capella":    24608,
    "Rigel":      24436,
    "Procyon":    37279,
    "Betelgeuse": 27989,
    "Achernar":    7588,
    "Aldebaran":  21421,
    "Antares":    80763,
    "Spica":      65474,
    "Pollux":     37826,
    "Fomalhaut": 113368,
    "Deneb":     102098,
    "Regulus":    49669,
    "Altair":     97649,
    "Polaris":    11767,
}
 
 
# --- astronomy -----------------------------------------------------------
 
class Sky:
    """Loads the ephemeris + star catalog once, resolves any target to (az, alt)."""
 
    def __init__(self, lat, lon):
        self.ts = load.timescale()
        self.eph = load("de421.bsp")
        self.site = self.eph["earth"] + wgs84.latlon(lat, lon)
        with load.open(hipparcos.URL) as f:
            self.stars_df = hipparcos.load_dataframe(f)
 
    def azalt(self, name):
        t = self.ts.now()
        if name in PLANETS:
            body = self.eph[PLANETS[name]]
        elif name in STARS:
            body = Star.from_dataframe(self.stars_df.loc[STARS[name]])
        else:
            raise ValueError(f"unknown target: {name}")
        alt, az, _ = self.site.at(t).observe(body).apparent().altaz()
        return az.degrees, alt.degrees
 
 
# --- pointing ------------------------------------------------------------
 
def point_at(mount, sky, offset, name):
    az_true, alt_true = sky.azalt(name)
    if alt_true < 0:
        print(f"{name} is below the horizon right now (alt {alt_true:.1f}).")
        return
    # command = true + calibration offset; mount applies the cable-flip internally
    mount.goto(az_true + offset[0], alt_true + offset[1])
    print(f"Pointing at {name}  (az {az_true:.1f}, alt {alt_true:.1f})")
 
 
# --- menu ----------------------------------------------------------------
 
def pick(title, names):
    print(f"\n{title}")
    for i, name in enumerate(names, 1):
        print(f"{i:2}. {name}")
    print(" 0. back")
    while True:
        choice = input("> ").strip()
        if choice == "0":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(names):
            return names[int(choice) - 1]
        print("Invalid choice.")
 
 
def menu(mount, sky, offset):
    while True:
        print("\n=== Laser target ===")
        print(" 1. Planets, Sun & Moon")
        print(" 2. Stars")
        print(" 0. quit")
        choice = input("> ").strip()
 
        if choice == "1":
            name = pick("Planets, Sun & Moon:", list(PLANETS))
        elif choice == "2":
            name = pick("Stars:", list(STARS))
        elif choice == "0":
            return
        else:
            print("Invalid choice.")
            continue
 
        if name:
            point_at(mount, sky, offset, name)
            
