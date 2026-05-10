// arduino_data_logger.ino
// Arduino Nano 33 BLE Sense Rev2
// Device-native HAR dataset logger

#include <Arduino_BMI270_BMM150.h>

const unsigned long SAMPLE_PERIOD_MS = 20;  // 50 Hz

String currentLabel = "UNLABELLED";

unsigned long lastSampleTime = 0;


void setup() {
  Serial.begin(115200);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("ERROR: IMU init failed");
    while (1);
  }

  Serial.println("READY");
}


void loop() {

  // ── 1. Check for an incoming label from Python ──────────────────────────
  //
  // readStringUntil('\n') blocks until '\n' arrives or the stream times out.
  // Using Serial.available() first avoids blocking the 50 Hz sample cadence
  // when no data is waiting.
  //
  // A non-empty line is treated as a new label; an empty line (e.g. a stray
  // '\r\n') is silently ignored so the previous label is preserved.

  if (Serial.available()) {
    String incoming = Serial.readStringUntil('\n');
    incoming.trim();

    if (incoming.length() > 0) {
      currentLabel = incoming;

      // ACK: echo the accepted label back so Python can confirm it
      // before it starts recording.  Format: "LABEL_SET:<label>"
      Serial.print("LABEL_SET:");
      Serial.println(currentLabel);
    }
  }


  if (millis() - lastSampleTime >= SAMPLE_PERIOD_MS) {
    lastSampleTime = millis();

    float ax, ay, az;
    float gx, gy, gz;

    if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {

      IMU.readAcceleration(ax, ay, az);
      IMU.readGyroscope(gx, gy, gz);

      // Timestamp taken after read so it reflects when data was actually
      // captured, not when the period fired.
      unsigned long ts = millis();

      // ── CSV row ───────────────────────────────────────────────────────
      Serial.print(ts);           Serial.print(",");
      Serial.print(currentLabel); Serial.print(",");
      Serial.print(ax, 6);        Serial.print(",");
      Serial.print(ay, 6);        Serial.print(",");
      Serial.print(az, 6);        Serial.print(",");
      Serial.print(gx, 6);        Serial.print(",");
      Serial.print(gy, 6);        Serial.print(",");
      Serial.println(gz, 6);
    }
  }
}
