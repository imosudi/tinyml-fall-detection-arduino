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

This repository demonstrates an end-to-end TinyML workflow for IMU-based human activity recognition:

- Device-native IMU data collection from Arduino
- Python-based dataset capture and CSV export
- Notebook-driven TensorFlow model development
- Int8 quantization for TFLite Micro deployment
- Arduino sketch for real-time labeled IMU logging

## Repository contents

- `arduino_data_logger.ino` - Arduino Nano 33 BLE Sense Rev2 sketch for IMU data logging.
- `data_capture.py` - Serial data capture script that labels data recordings and writes CSV files.
- `device_native_dataset/` - Recorded device-native IMU dataset files.
- `requirements.txt` - Python dependency list.
- `*.ipynb` - Prototype and quantized model training notebooks.

## Getting started

```bash
git clone https://github.com/imosudi/tinyml-fall-detection-arduino.git
cd tinyml-fall-detection-arduino
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> If you already have the repository checked out, run the `venv` and install steps from inside the project folder.

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


Connected to Arduino.

Available Labels:
  0: STATIONARY
  1: WALKING

Select label index (q to quit): 

5. Select the label index and recording duration.

Connected to Arduino.

Available Labels:
  0: STATIONARY
  1: WALKING

Select label index (q to quit): 1
Recording duration (seconds): 

6. The script sends the selected label to the Arduino and waits for a confirmation response.
7. Recorded CSV files are saved to `device_native_dataset/`.

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

## Deployment

This repository is focused on dataset collection and model prototyping. The next step is to convert a trained quantized model to TFLite Micro and deploy it to the Arduino platform.

## Project goals

- Capture labeled IMU data on-device
- Build a TinyML workflow for human activity and fall detection
- Enable efficient int8 inference on Arduino hardware
- Support future extension to UCI-HAR style activity classes



## License

This project is licensed under the **BSD 3-Clause License**. See [LICENSE](./LICENSE) for details.

## Author

**Mosudi Isiaka O.**  
📧 [mosudi.isiaka@gmail.com](mailto:mosudi.isiaka@gmail.com)  
💻 [https://github.com/imosudi](https://github.com/imosudi)
