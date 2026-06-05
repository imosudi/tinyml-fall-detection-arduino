# tinyml-fall-detection-arduino

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?logo=tensorflow&logoColor=white)
![TensorFlow Lite](https://img.shields.io/badge/TFLite-Micro-orange)
![TinyML](https://img.shields.io/badge/TinyML-Embedded_AI-green)
![Arduino](https://img.shields.io/badge/Arduino-Nano_33_BLE_Sense_Rev2-00979D?logo=arduino&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-ARM_Cortex--M4-blueviolet)
![MCU](https://img.shields.io/badge/MCU-nRF52840-red)
![Sensor](https://img.shields.io/badge/Sensor-BMI270_IMU-success)
![Edge AI](https://img.shields.io/badge/Edge_AI-Real_Time-informational)
![Activity Recognition](https://img.shields.io/badge/HAR-Activity_Recognition-yellowgreen)
![Fall Detection](https://img.shields.io/badge/Fall-Detection-critical)
![Inference](https://img.shields.io/badge/Inference-On_Device-brightgreen)
![Dataset](https://img.shields.io/badge/Dataset-UCI_HAR-lightgrey)
![Device Native](https://img.shields.io/badge/Data-Device_Native-blue)
![Quantization](https://img.shields.io/badge/Quantization-INT8-orange)
![Framework](https://img.shields.io/badge/Framework-TFLite_Micro-black)
![Google Colab](https://img.shields.io/badge/Google-Colab-F9AB00?logo=googlecolab&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-Ubuntu-E95420?logo=ubuntu&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Research_Prototype-blue)
![Research](https://img.shields.io/badge/Research-TinyML-important)
![Latency](https://img.shields.io/badge/Latency-<50ms-success)
![Sampling Rate](https://img.shields.io/badge/Sampling-50Hz-blue)
![Memory](https://img.shields.io/badge/SRAM-Constrained-red)
![Deployment](https://img.shields.io/badge/Deployment-Microcontroller-success)
![Serial Logging](https://img.shields.io/badge/Serial-CSV_Logging-lightgrey)
![Model](https://img.shields.io/badge/Model-Fully_Connected_NN-blue)
![Feature Engineering](https://img.shields.io/badge/Feature-Engineered-yellow)
![Edge Computing](https://img.shields.io/badge/Edge-Computing-9cf)
![IoT](https://img.shields.io/badge/IoT-Smart_Systems-ff69b4)
![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen)
![Made With](https://img.shields.io/badge/Made_with-Colab-orange)

Real-time fall and activity detection on an Arduino Nano 33 BLE Sense Rev2 using TinyML.

This repository demonstrates an end-to-end TinyML workflow for IMU-based activity recognition, and it is being adapted for veterinary post-operative monitoring. The same lightweight edge pipeline can support continuous recovery assessment for animals using a compact sensor collar or harness instead of subjective manual observation.

## System overview and memory layout

The project uses an event-driven TinyML pipeline that begins at the IMU, passes through a pre-filter gate, windowing, feature extraction, and quantized on-device inference. The visual block diagram is available in [images/architecture_block_diagram.png](images/architecture_block_diagram.png) and [images/architecture_block_diagram.svg](images/architecture_block_diagram.svg).

To understand deployment feasibility on the Nano 33 BLE Sense Rev2, the SRAM allocation view is provided in [images/SRAM_layout.png](images/SRAM_layout.png) and [images/SRAM_layout.svg](images/SRAM_layout.svg). These diagrams are important because the tensor arena, interpreter runtime, feature buffers, and stack usage must all fit inside the constrained SRAM budget of the microcontroller.

- Device-native IMU data collection from Arduino
- Python-based dataset capture and CSV export
- Notebook-driven TensorFlow model development
- Int8 quantization for TFLite Micro deployment
- Arduino sketch for real-time labeled IMU logging

## Veterinary application focus

### 1. Objective: Continuous Post-Operative Monitoring
Traditionally, assessing an animal's recovery relies on periodic, subjective visual observations by clinic staff. By adapting this system, a lightweight sensor collar or harness can continuously track a recovering animal 24/7 without human bias.

- Sedation and pain tracking: the system can classify subtle behavioral shifts. An animal experiencing breakthrough pain or prolonged sedation will show highly restricted movement, altering the expected baseline ratio of Stationary versus active states.
- Wound and device protection: sudden, repetitive jerk movements captured by the IMU can flag an animal aggressively scratching, biting, or shaking its head against a surgical site, cast, or Elizabethan collar.

### 2. Automated Animal Fall and Orthopedic Distress Alerts
For large animals (such as horses or cattle recovering from anesthesia) or small animals following major orthopedic or neurological surgeries, a fall can be catastrophic.

- Immediate trauma flags: using the pipeline's real-time fall detection algorithm, the system can instantly identify a high-G impact or a sudden change in spatial orientation followed by prolonged immobility.
- Recumbency warnings: if a postoperative patient falls or collapses and remains completely stationary for an abnormal duration, the edge device can trigger an automated alert to notify clinic staff immediately.

### 3. Quantitative Mobility and Gait Assessment
During orthopedic rehabilitation, a veterinarian needs to know if an animal is increasing its weight-bearing activity over time.

- Activity budgeting: the system can calculate a daily activity budget by quantifying how many minutes the animal spends walking versus resting.
- Gait integrity: changes in acceleration magnitude and variability during walking windows can act as a digital biomarker for lameness or asymmetric limb favoring.

### 4. Non-Invasive, Low-Stress Edge Intelligence (TinyML)
Animals in recovery are highly sensitive to stress, and traditional monitoring setups are often impractical.

- Ultra-lightweight design: the pipeline optimizes the neural network down to a compact INT8 TFLite Micro binary, allowing the intelligence loop to run directly on-device.
- Long battery life and low stress: the device can process data locally and only transmit alerts when anomalies occur, keeping the footprint small and unobtrusive.

This current attempt is starting from what is known before moving toward the unknown, working from datasets recovered from live animals.

## Project structure

```
tinyml-fall-detection-arduino
├── arduino_data_logger
│   └── arduino_data_logger.ino
├── data_capture.py
├── device_native_dataset
│   ├── STATIONARY_20260510_194427.csv
│   └── WALKING_20260510_193844.csv
├── device_native_training.ipynb
├── LICENSE
├── README.md
├── requirements.txt
├── screenshots
│   └── arduino_data_logger_upload.png
```

## Getting started

```bash
git clone https://github.com/imosudi/tinyml-fall-detection-arduino.git
cd tinyml-fall-detection-arduino
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> If you already have the repository checked out, run the `venv` and install steps from inside the project folder.
>
> **Note:** `requirements.txt` only includes dependencies for `data_capture.py` (e.g., `pyserial`). The notebooks were developed and run on Google Colab, so they require additional packages like TensorFlow, NumPy, Pandas, Matplotlib, Seaborn, Scikit-learn, etc. Install them separately if running notebooks locally.

## Requirements

- Python 3.9+ (tested with Python 3.11)
- `pyserial` for serial communication
- Arduino Nano 33 BLE Sense Rev2
- Arduino CLI or Arduino IDE for loading the sketch

Install Python dependencies:


## Data collection
1. Run: ./arduino-ide_2.3.8_Linux_64bit.AppImage --no-sandbox
    **Arduino IDE**: [Arduino IDE](screenshots/arduino_data_logger_upload.png)
2. Upload `arduino_data_logger/arduino_data_logger.ino` to the Arduino Nano 33 BLE Sense Rev2.
3. Connect the board to your computer via USB.
4. Update `SERIAL_PORT` in `data_capture.py` if your device is not on `/dev/ttyACM0`.
5. Run the capture script:

```bash
python data_capture.py
```

6. Select the label index and recording duration.
7. The script sends the selected label to the Arduino and waits for a confirmation response.
8. Recorded CSV files are saved to `device_native_dataset/`.

## Notes on data capture

- The Arduino sketch logs IMU samples at 50 Hz.
- Each CSV row contains: `timestamp_ms`, `label`, `ax`, `ay`, `az`, `gx`, `gy`, `gz`.
- The Python script discards warm-up samples after label acknowledgement to avoid unlabeled rows.

## Model development

Several notebooks are included for experimentation and quantization:

- `uci_har_prototype.ipynb`
- `uci_har_prototype_single_block.ipynb`
- `uci_har_prototype_quantised.ipynb`
- `uci_har_prototype_quantised_single_block.ipynb`
- `uci_har_prototype_stage2.ipynb`
- `device_native_training.ipynb`

Use these notebooks to explore feature engineering, model training, and TFLite quantization for deployment.

## Current challenge

The current classifier behavior shows a one-class prediction problem. The confusion matrix indicates the model is predicting only `STATIONARY`:

True Class	Predicted STATIONARY	Predicted WALKING
STATIONARY	120	0
WALKING	0	0

This means the model correctly classified 120 `STATIONARY` samples, but it did not produce any `WALKING` predictions.

Note: Already being resolved

## Deployment

This repository is focused on dataset collection and model prototyping. The next step is to convert a trained quantized model to TFLite Micro and deploy it to the Arduino platform.

## Project goals

- Capture labeled IMU data on-device
- Build a TinyML workflow for activity and fall detection
- Adapt the pipeline for veterinary recovery and distress monitoring
- Enable efficient int8 inference on Arduino hardware
- Support future extension to animal-activity and orthopedic rehabilitation use cases



## License

This project is licensed under the **BSD 3-Clause License**. See [LICENSE](./LICENSE) for details.

## Author

**Mosudi Isiaka O.**  
📧 [mosudi.isiaka@gmail.com](mailto:mosudi.isiaka@gmail.com)  
💻 [https://github.com/imosudi](https://github.com/imosudi)
