
/*
 * Real-Time Activity Recognition
 * Arduino Nano 33 BLE Sense Rev2
 * TensorFlow Lite Micro
 *
 * Classes:
 * 0 = STATIONARY
 * 1 = WALKING
 */

#include <Arduino_BMI270_BMM150.h>

#include "model.h"
#include "scaler.h"
#include "labels.h"

#include "TensorFlowLite.h"

#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/version.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"

// Built-in RGB LED (active LOW on Nano 33 BLE)
#define LED_RED   LEDR
#define LED_GREEN LEDG
#define LED_BLUE  LEDB

void setLED(bool r, bool g, bool b)
{
  digitalWrite(LED_RED,   r ? LOW : HIGH);
  digitalWrite(LED_GREEN, g ? LOW : HIGH);
  digitalWrite(LED_BLUE,  b ? LOW : HIGH);
}

// =====================================================
// Configuration
// =====================================================

constexpr int WINDOW_SIZE = 50;
constexpr int NUM_AXES = 6;
constexpr int NUM_FEATURES = 28;

constexpr float SAMPLE_RATE_HZ = 50.0f;
constexpr uint32_t SAMPLE_PERIOD_MS = 20;

constexpr float INPUT_SCALE = 0.06866828f;
constexpr int INPUT_ZERO_POINT = -71;

constexpr float OUTPUT_SCALE = 0.00390625f;
constexpr int OUTPUT_ZERO_POINT = -128;

constexpr float CONFIDENCE_THRESHOLD = 0.70f;

// =====================================================
// Tensor Arena
// =====================================================

constexpr int kTensorArenaSize = 16 * 1024;

uint8_t tensor_arena[kTensorArenaSize];

// =====================================================
// TFLM Objects
// =====================================================

const tflite::Model* model = nullptr;

tflite::MicroInterpreter* interpreter = nullptr;

TfLiteTensor* input = nullptr;
TfLiteTensor* output = nullptr;

// =====================================================
// Sensor Window Buffers
// =====================================================

float window_buffer[WINDOW_SIZE][NUM_AXES];

int sample_index = 0;

// =====================================================
// Feature Buffer
// =====================================================

float features[NUM_FEATURES];

// =====================================================
// Utility Functions
// =====================================================

float computeMean(float* data, int len)
{
  float sum = 0.0f;

  for (int i = 0; i < len; i++)
  {
    sum += data[i];
  }

  return sum / len;
}

float computeStd(float* data, int len, float mean)
{
  float var = 0.0f;

  for (int i = 0; i < len; i++)
  {
    float d = data[i] - mean;
    var += d * d;
  }

  return sqrt(var / len);
}

float computeMin(float* data, int len)
{
  float m = data[0];

  for (int i = 1; i < len; i++)
  {
    if (data[i] < m) m = data[i];
  }

  return m;
}

float computeMax(float* data, int len)
{
  float m = data[0];

  for (int i = 1; i < len; i++)
  {
    if (data[i] > m) m = data[i];
  }

  return m;
}

// =====================================================
// Feature Extraction
// Must match Python implementation exactly
// =====================================================

void extractFeatures()
{
  int feature_idx = 0;

  float axis_data[WINDOW_SIZE];

  // Mean + Std

  for (int axis = 0; axis < 6; axis++)
  {
    for (int i = 0; i < WINDOW_SIZE; i++)
    {
      axis_data[i] = window_buffer[i][axis];
    }

    float mean = computeMean(axis_data, WINDOW_SIZE);
    float stdv = computeStd(axis_data, WINDOW_SIZE, mean);

    features[feature_idx++] = mean;
    features[feature_idx++] = stdv;
  }

  // Min + Max

  for (int axis = 0; axis < 6; axis++)
  {
    for (int i = 0; i < WINDOW_SIZE; i++)
    {
      axis_data[i] = window_buffer[i][axis];
    }

    features[feature_idx++] =
      computeMin(axis_data, WINDOW_SIZE);

    features[feature_idx++] =
      computeMax(axis_data, WINDOW_SIZE);
  }

  // Mean absolute acceleration

  float abs_acc_sum = 0.0f;

  for (int i = 0; i < WINDOW_SIZE; i++)
  {
    abs_acc_sum +=
      fabs(window_buffer[i][0]) +
      fabs(window_buffer[i][1]) +
      fabs(window_buffer[i][2]);
  }

  features[feature_idx++] =
    abs_acc_sum / WINDOW_SIZE;

  // Mean absolute gyro

  float abs_gyro_sum = 0.0f;

  for (int i = 0; i < WINDOW_SIZE; i++)
  {
    abs_gyro_sum +=
      fabs(window_buffer[i][3]) +
      fabs(window_buffer[i][4]) +
      fabs(window_buffer[i][5]);
  }

  features[feature_idx++] =
    abs_gyro_sum / WINDOW_SIZE;

  // Acc magnitude

  float mags[WINDOW_SIZE];

  for (int i = 0; i < WINDOW_SIZE; i++)
  {
    float ax = window_buffer[i][0];
    float ay = window_buffer[i][1];
    float az = window_buffer[i][2];

    mags[i] =
      sqrt(ax * ax + ay * ay + az * az);
  }

  float mag_mean =
    computeMean(mags, WINDOW_SIZE);

  float mag_std =
    computeStd(mags, WINDOW_SIZE, mag_mean);

  features[feature_idx++] = mag_mean;
  features[feature_idx++] = mag_std;
}

// =====================================================
// Scaling + Quantization
// =====================================================

void prepareInputTensor()
{
  for (int i = 0; i < NUM_FEATURES; i++)
  {
    float scaled =
      (features[i] - scaler_mean[i])
      /
      scaler_scale[i];

    int8_t q =
      round(
        scaled / INPUT_SCALE
      ) + INPUT_ZERO_POINT;

    q = constrain(q, -128, 127);

    input->data.int8[i] = q;
  }
}

// =====================================================
// Inference
// =====================================================

void runInference()
{
  extractFeatures();

  prepareInputTensor();

  uint32_t start_us = micros();

  TfLiteStatus invoke_status =
    interpreter->Invoke();

  uint32_t end_us = micros();

  if (invoke_status != kTfLiteOk)
  {
    Serial.println("Inference failed");
    return;
  }

  float probs[2];

  for (int i = 0; i < 2; i++)
  {
    probs[i] =
      (output->data.int8[i]
      -
      OUTPUT_ZERO_POINT)
      *
      OUTPUT_SCALE;
  }

  int predicted = 0;

  if (probs[1] > probs[0])
  {
    predicted = 1;
  }

  float confidence =
    max(probs[0], probs[1]);

  if (confidence >= CONFIDENCE_THRESHOLD)
    {
      Serial.print("Prediction: ");
      Serial.print(LABELS[predicted]);
      Serial.print(" | Confidence: ");
      Serial.print(confidence, 3);
      Serial.print(" | Latency(us): ");
      Serial.println(end_us - start_us);

      if (predicted == 0)
      {
        // STATIONARY — blue
        setLED(false, false, true);
      }
      else if (predicted == 1)
      {
        // WALKING — green
        setLED(false, true, false);
      }
      else
      {
        // Below threshold or unknown — LED off
        setLED(false, false, true);
      }
    }
    else
    {
      setLED(false, false, false); // uncertain — off
    }
}

// =====================================================
// Setup
// =====================================================

void setup()
{
  Serial.begin(115200);
  pinMode(LED_RED,   OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_BLUE,  OUTPUT);
  setLED(false, false, false); // all off
  while (!Serial);

  if (!IMU.begin())
  {
    Serial.println("IMU init failed");
    while (1);
  }

  model = tflite::GetModel(arduino_inference_device_native_model_int8_tflite);

  static tflite::MicroErrorReporter micro_error_reporter;

  static tflite::MicroMutableOpResolver<2> resolver;
  resolver.AddFullyConnected();
  resolver.AddSoftmax();

  static tflite::MicroInterpreter static_interpreter(
    model,
    resolver,
    tensor_arena,
    kTensorArenaSize,
    &micro_error_reporter
  );

  interpreter = &static_interpreter;
  interpreter->AllocateTensors();

  input  = interpreter->input(0);
  output = interpreter->output(0);

  Serial.println("System Ready");
}
// =====================================================
// Main Loop
// =====================================================

void loop()
{
  float ax, ay, az;
  float gx, gy, gz;

  if (IMU.accelerationAvailable() &&
      IMU.gyroscopeAvailable())
  {
    IMU.readAcceleration(
      ax, ay, az);

    IMU.readGyroscope(
      gx, gy, gz);

    window_buffer[sample_index][0] = ax;
    window_buffer[sample_index][1] = ay;
    window_buffer[sample_index][2] = az;

    window_buffer[sample_index][3] = gx;
    window_buffer[sample_index][4] = gy;
    window_buffer[sample_index][5] = gz;

    sample_index++;

    if (sample_index >= WINDOW_SIZE)
    {
      runInference();

      sample_index = 0;
    }
  }

  delay(SAMPLE_PERIOD_MS);
}