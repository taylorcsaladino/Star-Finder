"""
Mount: the one hardware-abstraction class the whole project talks to.

Wraps the serial link and the flip logic. Everything above it (home, calibration,
menu) works in TRUE az/alt and never thinks about the wire protocol or the cable-flip.
"""

from Serial_connect import connection, serial_comm
from solve_angles import solve_angles, inverse_solve_angles


class Mount:
    def __init__(self, port, baud=115200):
        self.arduino = connection(port, baud)
        if self.arduino is None:
            raise RuntimeError(f"could not open {port}")

    # --- lifecycle ---
    def close(self):
        # always release the serial port so a crashed/interrupted run
        # does not leave COM held (which causes 'Access is denied' next time)
        if getattr(self, "arduino", None) is not None:
            self.arduino.close()
            self.arduino = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def __del__(self):
        # best-effort backstop if close() was never called
        try:
            self.close()
        except Exception:
            pass

    # --- low level ---
    def _send(self, message):
        return serial_comm(self.arduino, message)

    def _read_line(self):
        # read one more framed line without sending a new command
        try:
            return self.arduino.readline().decode().strip()
        except Exception:
            return ""

    # --- movement ---
    def nudge(self, axis, direction):
        # axis: 'az' or 'alt'; direction: +1 / -1
        sign = "+" if direction > 0 else "-"
        self._send(f"NUDGE:{axis.upper()}{sign}")

    def goto(self, az, alt):
        # az/alt are calibrated TRUE angles. The cable-flip is applied HERE only,
        # so the stored calibration offset stays in the raw frame.
        motor_az, motor_alt = solve_angles(az, alt)
        self._send(f"GOTO:AZ={motor_az:.2f},ALT={motor_alt:.2f}")

    def goto_raw(self, az, alt):
        # used by calibration (uncalibrated command). Same wire path as goto:
        # the flip is applied here, and read_position() inverts it, so
        # calibration works for objects in EITHER hemisphere.
        self.goto(az, alt)

    # --- feedback ---
    def read_position(self):
        # Drop any stale replies still in the buffer (e.g. a late <OK> from a
        # long GOTO that outran the read timeout) so we read a FRESH POS frame.
        try:
            self.arduino.reset_input_buffer()
        except Exception:
            pass

        reply = self._send("POS?")            # want <POS:AZ=123.40,ALT=45.00>
        # If we still got a stray frame (<OK>, <READY>, empty, ...), keep
        # reading lines until a real POS frame shows up.
        for _ in range(6):
            if reply and "AZ=" in reply and "ALT=" in reply:
                break
            reply = self._read_line()
        else:
            raise RuntimeError(f"no POS reply from Arduino (last: {reply!r})")

        body = reply.strip("<>").replace("POS:", "")
        parts = dict(p.split("=") for p in body.split(","))
        motor_az, motor_alt = float(parts["AZ"]), float(parts["ALT"])
        # The Arduino reports MOTOR angles (post-flip). Convert back to TRUE
        # az/alt so callers (calibration, etc.) never see the cable-flip and
        # can difference against sky coordinates in a single consistent frame.
        return inverse_solve_angles(motor_az, motor_alt)

    def set_zero(self):
        self._send("ZERO")                    # current pose becomes (0, 0)
