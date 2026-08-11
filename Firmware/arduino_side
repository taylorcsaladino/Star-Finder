// Arduino side: parse commands from Python, move motors, report position.
// Wire protocol (newline-terminated):
//   GOTO:AZ=123.40,ALT=45.00   -> <OK>
//   NUDGE:AZ+ / AZ- / ALT+ / ALT-  -> <OK>
//   ZERO                        -> <OK>   (current pose becomes 0,0)
//   HOME                        -> <OK>   (drive back to 0,0)
//   POS?                        -> <POS:AZ=..,ALT=..>
//
// Motors: two CL42T closed-loop stepper drivers, STEP/DIR interface via AccelStepper.
//   Top motor    (ALT axis): STEP = D2, DIR = D4   (CL42T PUL- = D2, DIR- = D4)
//   Bottom motor (AZ  axis): STEP = D3, DIR = D5   (CL42T PUL- = D3, DIR- = D5)
//   CL42T PUL+ and DIR+ must be tied to +5V (common-anode), NOT GND.
//
// Install the AccelStepper library first:
//   Arduino IDE -> Tools -> Manage Libraries -> search "AccelStepper" -> Install.

#include <AccelStepper.h>

// ---- pins ---------------------------------------------------------------

const int ALT_STEP = 3;   // PUL- on the altitude motor's driver
const int ALT_DIR  = 5;   // DIR- on the altitude motor's driver
const int AZ_STEP  = 2;   // PUL- on the azimuth motor's driver
const int AZ_DIR   = 4;   // DIR- on the azimuth motor's driver

// ---- gearing: degrees -> steps ------------------------------------------
// STEPS_PER_REV = pulses per motor revolution set by the CL42T DIP switches
//   (the "pulse/rev" bank). Read it off the driver and put the number here.
// GEAR_RATIO    = axis-turns reduction between motor shaft and the actual
//   az/alt axis (e.g. 5.0 if a 5:1 gearbox/belt; 1.0 if direct-drive).
const float STEPS_PER_REV = 3200.0;   // <-- SET to your CL42T DIP setting
const float GEAR_RATIO    = 1.0;      // <-- SET to your mechanical reduction
const float STEPS_PER_DEG = (STEPS_PER_REV * GEAR_RATIO) / 360.0;

// ---- motion profile (tune to taste) -------------------------------------
const float MAX_SPEED = 1200.0;   // steps/sec
const float ACCEL     = 600.0;    // steps/sec^2

const float NUDGE_STEP = 0.5;     // degrees per nudge (tune to your gearing)

AccelStepper azMotor (AccelStepper::DRIVER, AZ_STEP,  AZ_DIR);
AccelStepper altMotor(AccelStepper::DRIVER, ALT_STEP, ALT_DIR);

float currentAz  = 0.0;
float currentAlt = 0.0;

// ---- helpers ------------------------------------------------------------
long degToSteps(float deg) {
  return lround(deg * STEPS_PER_DEG);
}

void moveMotorsTo(float az, float alt) {
  // Absolute move: both axes run concurrently until they reach target.
  // If an axis turns the WRONG way, flip its DIR: e.g.
  //   azMotor.setPinsInverted(true, false, false);  // (dir, step, enable)
  azMotor.moveTo(degToSteps(az));
  altMotor.moveTo(degToSteps(alt));
  while (azMotor.distanceToGo() != 0 || altMotor.distanceToGo() != 0) {
    azMotor.run();
    altMotor.run();
  }
  currentAz  = azMotor.currentPosition()  / STEPS_PER_DEG;
  currentAlt = altMotor.currentPosition() / STEPS_PER_DEG;
}

void readEncoders() {
  // CL42T closes the loop internally; it does not report position back to the
  // Arduino unless you wire its ALM/encoder output. So we report the commanded
  // step position, which is accurate as long as no faults occurred.
  currentAz  = azMotor.currentPosition()  / STEPS_PER_DEG;
  currentAlt = altMotor.currentPosition() / STEPS_PER_DEG;
}
// -------------------------------------------------------------------------

void setup() {
  Serial.begin(115200);

  azMotor.setMaxSpeed(MAX_SPEED);
  azMotor.setAcceleration(ACCEL);
  altMotor.setMaxSpeed(MAX_SPEED);
  altMotor.setAcceleration(ACCEL);

  // CL42T inputs are optocoupled: AccelStepper's default ~1us STEP pulse is
  
  azMotor.setMinPulseWidth(5);   // microseconds
  altMotor.setMinPulseWidth(5);

  // Altitude axis was mirrored (commanded +alt drove the laser DOWN), so its
  // direction is reversed here. Args are (directionInvert, stepInvert, enableInvert).
  // If the alt axis ends up moving the wrong way, flip this true<->false.
  altMotor.setPinsInverted(true, false, false);
  // If the azimuth axis is ever reversed too, uncomment the matching line:
  // azMotor.setPinsInverted(true, false, false);

  Serial.println("<READY>");
}

void loop() {
  if (Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg.startsWith("GOTO:")) {
      int aIdx = msg.indexOf("AZ=");
      int lIdx = msg.indexOf("ALT=");
      float az  = msg.substring(aIdx + 3, msg.indexOf(',', aIdx)).toFloat();
      float alt = msg.substring(lIdx + 4).toFloat();
      moveMotorsTo(az, alt);
      Serial.println("<OK>");
    }
    else if (msg == "NUDGE:AZ+")  { moveMotorsTo(currentAz + NUDGE_STEP, currentAlt); Serial.println("<OK>"); }
    else if (msg == "NUDGE:AZ-")  { moveMotorsTo(currentAz - NUDGE_STEP, currentAlt); Serial.println("<OK>"); }
    else if (msg == "NUDGE:ALT+") { moveMotorsTo(currentAz, currentAlt + NUDGE_STEP); Serial.println("<OK>"); }
    else if (msg == "NUDGE:ALT-") { moveMotorsTo(currentAz, currentAlt - NUDGE_STEP); Serial.println("<OK>"); }
    else if (msg == "ZERO") {
      // Current pose becomes the new (0,0) reference.
      azMotor.setCurrentPosition(0);
      altMotor.setCurrentPosition(0);
      currentAz = 0.0; currentAlt = 0.0;
      Serial.println("<OK>");
    }
    else if (msg == "HOME") {
      moveMotorsTo(0.0, 0.0);
      Serial.println("<OK>");
    }
    else if (msg == "POS?") {
      readEncoders();
      Serial.print("<POS:AZ=");
      Serial.print(currentAz, 2);
      Serial.print(",ALT=");
      Serial.print(currentAlt, 2);
      Serial.println(">");
    }
    else {
      Serial.println("<ERR:Unknown Command>");
    }
  }
}
