# data_capture.py
# This script captures data via serial from an Arduino device and saves it to CSV files for each activity label.
# My current target classes are "STATIONARY" and "WALKING".
# I intend to implemenT Ddata capture over BLE to make it flexible for collectiing the six target classes:
#  "WALKING", "WALKING_UP", "WALKING_DOWN", "SITTING", "STANDING", "LAYING".
import serial
import csv
import time
import os
from datetime import datetime

# CONFIG

SERIAL_PORT = "/dev/ttyACM0" 
BAUD_RATE = 115200

OUTPUT_DIR = "device_native_dataset"

TARGET_CLASSES = [
    "STATIONARY",
    "WALKING"
]

# SETUP

os.makedirs(OUTPUT_DIR, exist_ok=True)

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

time.sleep(3)

print("\nConnected to Arduino.")

# Flush startup messages
ser.reset_input_buffer()

# RECORD LOOP

while True:

    print("\nAvailable Labels:")
    for idx, label in enumerate(TARGET_CLASSES):
        print(f"{idx}: {label}")

    label_index = input("\nSelect label index (q to quit): ")

    if label_index.lower() == "q":
        break

    try:
        label = TARGET_CLASSES[int(label_index)]
    except:
        print("Invalid selection.")
        continue

    duration = int(input("Recording duration (seconds): "))

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{label}_{timestamp}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)

    print(f"\nRecording: {label}")
    print(f"Saving to: {filepath}")

    # Send label to Arduino
    ser.write((label + "\n").encode())

    start_time = time.time()

    sample_count = 0

    with open(filepath, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "timestamp_ms",
            "label",
            "ax",
            "ay",
            "az",
            "gx",
            "gy",
            "gz"
        ])

        while (time.time() - start_time) < duration:

            try:
                line = ser.readline().decode().strip()

                if not line:
                    continue

                parts = line.split(",")

                if len(parts) != 8:
                    continue

                writer.writerow(parts)

                sample_count += 1

                if sample_count % 50 == 0:
                    print(f"Captured {sample_count} samples")

            except KeyboardInterrupt:
                break

            except Exception as e:
                print("Read error:", e)

    print(f"\nFinished recording.")
    print(f"Total samples: {sample_count}")

ser.close()

print("\nSerial connection closed.")