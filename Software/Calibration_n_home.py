"""
home() and calibration().
 
home()        -> aim at true north/horizon with compass+level, store as (0,0).
calibration() -> point at two objects, record the raw az/alt offset.
 
Takes a live Mount (mount.py) and a Sky (Starmenu.py). No placeholders.
"""
 
 
# --- shared nudge helper -------------------------------------------------
 
def nudge_loop(mount):
    """Type w/a/s/d (any number per line), press Enter to apply, 'q' to finish."""
    print("Nudge: w/s = top motor (alt +/-), a/d = bottom motor (az -/+), q = done")
    while True:
        keys = input("> ").strip().lower()
        for k in keys:
            if k == "q":
                return
            elif k == "w":
                mount.nudge("alt", +1)
            elif k == "s":
                mount.nudge("alt", -1)
            elif k == "a":
                mount.nudge("az", -1)
            elif k == "d":
                mount.nudge("az", +1)
 
 
# --- home ----------------------------------------------------------------
 
def home(mount):
    """Aim the laser at true north on the horizon, then store that as (0, 0)."""
    while True:
        choice = input("Is the laser pointing true north and level? (y/n) ").strip().lower()
        if choice == "y":
            break
        elif choice == "n":
            print("Use the compass and level to aim it, then press q.")
            nudge_loop(mount)
        else:
            print("Invalid input.")
 
    mount.set_zero()
    print("Home set.")
 
 
# --- calibration ---------------------------------------------------------
 
def calibrate_object(mount, sky, target):
    """Point at one object, let the user correct it, return the raw (az, alt) difference."""
    az_true, alt_true = sky.azalt(target)
    mount.goto_raw(az_true, alt_true)  # uncalibrated command
 
    while True:
        ans = input(f"Is the laser on {target}? (y/n) ").strip().lower()
        if ans == "y":
            break
        elif ans == "n":
            nudge_loop(mount)
        else:
            print("Invalid input.")
 
    az_enc, alt_enc = mount.read_position()
    # difference between where it actually had to point and the true location
    az_diff = az_enc - az_true
    alt_diff = alt_enc - alt_true
    return (az_diff, alt_diff)
 
 
def combine(diff1, diff2):
    # TODO (your rule): how the two objects' differences become one offset.
    # Placeholder = average of the two.
    az_off = (diff1[0] + diff2[0]) / 2
    alt_off = (diff1[1] + diff2[1]) / 2
    return (az_off, alt_off)
 
 
def calibration(mount, sky):
    """Calibrate from two objects, return the stored (az, alt) offset."""
    first = input("First object to calibrate on: ").strip()
    diff1 = calibrate_object(mount, sky, first)
 
    second = input("Second object to calibrate on: ").strip()
    diff2 = calibrate_object(mount, sky, second)
 
    offset = combine(diff1, diff2)
    print(f"Calibration offset: az {offset[0]:+.3f}, alt {offset[1]:+.3f}")
    return offset
