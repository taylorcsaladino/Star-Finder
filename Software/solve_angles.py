def solve_angles(az, alt):
    # Beats the 180-deg base limit: for targets in the far hemisphere, aim the base
    # at the opposite heading and swing the altitude axis over the top. Keeps cables
    # from tangling. Returns MOTOR angles.
    az = az % 360

    if az <= 180:
        motor_az = az
        motor_alt = alt
    else:  # az > 180
        motor_az = az - 180
        motor_alt = 180 - alt

    return motor_az, motor_alt


def inverse_solve_angles(motor_az, motor_alt):
    # Inverse of solve_angles: convert MOTOR angles back to TRUE az/alt.
    # A flipped (far-hemisphere) target is the one whose altitude axis went
    # over the top (motor_alt > 90); a direct target keeps alt in 0..90.
    if motor_alt <= 90:
        az = motor_az
        alt = motor_alt
    else:  # over-the-top: this was a flipped command
        az = motor_az + 180
        alt = 180 - motor_alt

    return az % 360, alt
