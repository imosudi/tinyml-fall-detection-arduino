# data_capture.py
# Captures IMU data via serial from an Arduino device and saves it to CSV files.
# Current target classes: "STATIONARY", "WALKING"
# Planned BLE extension for six UCI-HAR classes:
#   "WALKING", "WALKING_UP", "WALKING_DOWN", "SITTING", "STANDING", "LAYING"

import serial
import csv
import time
import os
from datetime import datetime


SERIAL_PORT  = "/dev/ttyACM0"
BAUD_RATE    = 115200
OUTPUT_DIR   = "device_native_dataset"

TARGET_CLASSES = [
    "STATIONARY",
    "WALKING",
]

# How long to wait for the Arduino to ACK the label (seconds)
LABEL_ACK_TIMEOUT = 3.0

# Samples to discard after ACK — lets the IMU settle and ensures
# no UNLABELLED rows slip into the recording
WARMUP_SAMPLES = 25  # ~0.5 s at 50 Hz


os.makedirs(OUTPUT_DIR, exist_ok=True)

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(3)
ser.reset_input_buffer()
print("\nConnected to Arduino.")



def send_label_and_wait_for_ack(label: str) -> bool:
    """
    Send label to Arduino and wait for it to echo back:
        LABEL_SET:<label>
    Returns True on success, False on timeout.

    Requires the Arduino sketch to respond with:
        Serial.print("LABEL_SET:");
        Serial.println(currentLabel);
    after updating currentLabel.
    """
    ser.reset_input_buffer()
    ser.write((label + "\n").encode())

    deadline = time.time() + LABEL_ACK_TIMEOUT
    while time.time() < deadline:
        raw = ser.readline()
        if not raw:
            continue
        line = raw.decode(errors="replace").strip()
        if line.startswith("LABEL_SET:"):
            received = line.split(":", 1)[1].strip()
            if received == label:
                return True
            print(f"  [warn] Arduino ACK'd wrong label: '{received}' (expected '{label}')")
            return False

    return False  # timeout


def flush_warmup_samples(n: int) -> None:
    """Discard the first n data lines so no UNLABELLED rows enter the CSV."""
    discarded = 0
    while discarded < n:
        raw = ser.readline()
        if not raw:
            continue
        line = raw.decode(errors="replace").strip()
        parts = line.split(",")
        if len(parts) == 8:   # looks like a data row
            discarded += 1


def validate_csv_labels(filepath: str, expected_label: str) -> dict:
    """
    Read back the just-written CSV and report any label anomalies.
    Returns a dict: { label_value: count }
    """
    label_counts: dict = {}
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lbl = row.get("label", "").strip()
            label_counts[lbl] = label_counts.get(lbl, 0) + 1
    return label_counts



while True:

    print("\nAvailable Labels:")
    for idx, label in enumerate(TARGET_CLASSES):
        print(f"  {idx}: {label}")

    label_index = input("\nSelect label index (q to quit): ").strip()

    if label_index.lower() == "q":
        break

    try:
        label = TARGET_CLASSES[int(label_index)]
    except (ValueError, IndexError):
        print("Invalid selection.")
        continue

    try:
        duration = int(input("Recording duration (seconds): ").strip())
        if duration <= 0:
            raise ValueError
    except ValueError:
        print("Invalid duration.")
        continue

    print(f"\nSending label '{label}' to Arduino...")
    if not send_label_and_wait_for_ack(label):
        print(
            "[ERROR] Arduino did not acknowledge the label within "
            f"{LABEL_ACK_TIMEOUT:.0f} s.\n"
            "  • Check that the sketch sends 'LABEL_SET:<label>\\n'.\n"
            "  • Check the serial connection.\n"
            "Recording aborted."
        )
        continue
    print(f"  Arduino confirmed label: {label}")

    print(f"  Flushing {WARMUP_SAMPLES} warmup samples...")
    flush_warmup_samples(WARMUP_SAMPLES)
    print("  Ready.\n")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{label}_{timestamp}.csv"
    filepath  = os.path.join(OUTPUT_DIR, filename)

    print(f"Recording : {label}")
    print(f"Duration  : {duration} s")
    print(f"Output    : {filepath}\n")

    start_time   = time.time()
    sample_count = 0

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp_ms",
            "label",
            "ax", "ay", "az",
            "gx", "gy", "gz",
        ])

        while (time.time() - start_time) < duration:
            try:
                raw = ser.readline()
                if not raw:
                    continue

                line = raw.decode(errors="replace").strip()

                # Skip ACK lines or anything that isn't a data row
                if not line or line.startswith("LABEL_SET:"):
                    continue

                parts = line.split(",")
                if len(parts) != 8:
                    continue

                writer.writerow(parts)
                sample_count += 1

                if sample_count % 50 == 0:
                    elapsed = time.time() - start_time
                    print(f"  {sample_count} samples  ({elapsed:.1f} / {duration} s)")

            except KeyboardInterrupt:
                print("\nRecording interrupted by user.")
                break
            except Exception as e:
                print(f"  Read error: {e}")

    print(f"\nFinished. Total samples: {sample_count}")

    label_counts = validate_csv_labels(filepath, label)
    unexpected   = {k: v for k, v in label_counts.items() if k != label}

    if not label_counts:
        print("[WARN] CSV appears empty — no data rows written.")
    elif unexpected:
        print("\n[WARN] Unexpected labels found in CSV:")
        for k, v in unexpected.items():
            pct = v / sample_count * 100
            print(f"  '{k}': {v} rows ({pct:.1f} %)")
        print(
            "  This means the Arduino was still using the old label for some rows.\n"
            "  Consider deleting this file and re-recording."
        )
    else:
        good = label_counts.get(label, 0)
        print(f"[OK] All {good} rows correctly labeled '{label}'.")


ser.close()
print("\nSerial connection closed.")