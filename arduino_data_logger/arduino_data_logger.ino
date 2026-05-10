// arduino_data_logger.ino
// Arduino Nano 33 BLE Sense Rev2
// Device-native HAR dataset logger

#include <Arduino_BMI270_BMM150.h>

const float SAMPLE_RATE_HZ = 50.0;
const unsigned long SAMPLE_PERIOD_MS = 20;

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

  // Receive label updates from Python
  if (Serial.available()) {
    currentLabel = Serial.readStringUntil('\n');
    currentLabel.trim();
  }

  // Maintain 50 Hz sampling
  if (millis() - lastSampleTime >= SAMPLE_PERIOD_MS) {
    lastSampleTime = millis();

    float ax, ay, az;
    float gx, gy, gz;

    if (IMU.accelerationAvailable() &&
        IMU.gyroscopeAvailable()) {

      IMU.readAcceleration(ax, ay, az);
      IMU.readGyroscope(gx, gy, gz);

      unsigned long ts = millis();

      // CSV output
      Serial.print(ts);
      Serial.print(",");

      Serial.print(currentLabel);
      Serial.print(",");

      Serial.print(ax, 6);
      Serial.print(",");

      Serial.print(ay, 6);
      Serial.print(",");

      Serial.print(az, 6);
      Serial.print(",");

      Serial.print(gx, 6);
      Serial.print(",");

      Serial.print(gy, 6);
      Serial.print(",");

      Serial.println(gz, 6);
    }
  }
}