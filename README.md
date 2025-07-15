# Overview
**EchoSight: AI-Powered Wearable for the Visually Impaired**
EchoSight is a low-cost, compact, and intelligent wearable system designed to enhance spatial awareness and mobility for people with visual impairments. It integrates multiple technologies—including object detection, face recognition, and ultrasonic sensing—within an energy-efficient embedded architecture. The system operates in real-time, translating visual and spatial information into verbal feedback via a small audio module and headphones.
At the core of EchoSight are two microcontrollers:
* ESP32-CAM: Captures image frames and runs AI inference using a quantized YOLOv4-tiny model and Dlib-based facial recognition.

* NodeMCU ESP8266: Manages system logic, plays corresponding audio cues through the DFPlayer Mini, and handles ultrasonic obstacle alerts.

Together, these components deliver multimodal awareness to the user without requiring internet connectivity or bulky hardware. The system was developed with a strong focus on affordability, portability, and real-world usability, and has been validated through both lab testing and pilot user trials.


# Hardware Setup and Assembly
Before running the code, ensure that:
All components are properly wired and connected.
You have:
  * ESP32-CAM (for image-based AI)

  * NodeMCU ESP8266 (for control + audio)

  * DFPlayer Mini + speaker/headphone

  * HC-SR04 ultrasonic sensor


# Firmware Development and Flashing
The device operates using two microcontrollers, each flashed with dedicated firmware using the Arduino IDE.

### ESP32-CAM Firmware
The ESP32-CAM handles all image-based inference tasks. The firmware must include:
* Camera initialization routines.

* A quantized YOLOv4-tiny model (in TensorFlow Lite format).

* A Dlib-based face recognition module.

* Logic to capture frames, run inference, and output results via Serial or Wi-Fi.

**Steps:**

  * Install the ESP32 board package in Arduino IDE.

  * Set the board to "AI Thinker ESP32-CAM" and choose the correct COM port.

  * Flash the code using an FTDI programmer (connect GPIO0 to GND during upload).

  * Once uploaded, disconnect GPIO0 and reset the board to begin execution.

The ESP32 will continuously analyze images and send result labels (e.g., “Person Left”, “Chair Ahead”) to the NodeMCU for further processing.

### NodeMCU ESP8266 Firmware
The NodeMCU controls:

* Audio output via the DFPlayer Mini.

* Ultrasonic distance measurement.

* Optional transmission of sensor data to a Python-based central server.

**Steps:**

  * Install the ESP8266 board package in Arduino IDE.

  * Set the board to "NodeMCU 1.0 (ESP-12E Module)".

  * Flash the firmware via USB.

The NodeMCU interprets the object/face labels and maps them to predefined audio MP3s (e.g., “001.mp3” = “Obstacle ahead”) and triggers playback via serial commands to the DFPlayer Mini. It also continuously monitors the ultrasonic sensor to detect physical obstacles and trigger alerts independently if needed.

In the EchoSight repository, the file `node.cpp` contains the complete Arduino-compatible C++ code for the NodeMCU ESP8266 microcontroller. This microcontroller is responsible for several key functions in the system:

 * Interfacing with the DFPlayer Mini: It sends UART commands to play specific MP3 audio files based on received labels (e.g., "Obstacle Ahead").

 * Reading data from the HC-SR04 ultrasonic sensor: It continuously monitors the surroundings for obstacles and triggers warnings when nearby objects are detected.

 * Receiving detection results from ESP32-CAM: It processes incoming serial data sent by the ESP32 after running object or face detection.

 * Sending detection data to a Python backend `main.py`: It establishes a Wi-Fi connection and transmits key detection labels and alerts to a server via HTTP POST requests.

 * The `node.cpp` file is structured as an Arduino sketch (a `.ino` file in disguise), containing standard `setup()` and `loop()` functions required by Arduino’s microcontroller runtime.


### Setting Up Arduino IDE for NodeMCU
Before flashing the code in `node.cpp` onto the NodeMCU, the Arduino IDE must be configured appropriately to support the `ESP8266` board. This involves installing the board definitions and selecting the correct options.

**Step-by-Step Configuration:**
1. Install Arduino IDE

    * Download and install the Arduino IDE from the official Arduino website [www.arduino.cc](https://www.arduino.cc/en/software).

2. Install ESP8266 Board Support

    * Open Arduino IDE.
    
    * Navigate to: `File` → `Preferences`.

In the Additional Board Manager URLs field, add:

```http://arduino.esp8266.com/stable/package_esp8266com_index.json```

   * Then go to: `Tools` → `Board` → `Boards Manager`.

   * Search for ESP8266 and click Install.

