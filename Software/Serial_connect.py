import serial
import time


## opening port to arduino ##

def connection(port, baud_rate=115200):
    try:
        # timeout=5 so a long blocking GOTO can finish and return its <OK>
        # before readline() gives up (a 2 s timeout desynced the request/reply
        # pairing and left stale frames in the buffer).
        arduino = serial.Serial(port, baud_rate, timeout=5)
        time.sleep(2)              # let the Arduino reset
        arduino.reset_input_buffer()
        arduino.readline()         # consume the <READY> boot line
        return arduino
    except serial.SerialException as e:
        print(f"error connecting to arduino on {port}: {e}")
        return None


## send one command, return the Arduino's reply ##

def serial_comm(connection, message):
    try:
        connection.write((message + "\n").encode())   # newline terminates the command
        response = connection.readline().decode().strip()
        return response
    except serial.SerialException as e:
        print(f"error talking to arduino: {e}")
        return None


if __name__ == "__main__":
    arduino = connection("COM3", 115200)
    if arduino:
        print("Response:", serial_comm(arduino, "HOME"))
