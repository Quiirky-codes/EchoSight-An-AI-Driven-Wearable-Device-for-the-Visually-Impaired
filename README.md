# Overview
**EchoSight: AI-Powered Wearable for the Visually Impaired**
EchoSight is a low-cost, compact, and intelligent wearable system designed to enhance spatial awareness and mobility for people with visual impairments. It integrates multiple technologies—including object detection, face recognition, and ultrasonic sensing—within an energy-efficient embedded architecture. The system operates in real-time, translating visual and spatial information into verbal feedback via a small audio module and headphones.
At the core of EchoSight are two microcontrollers:
* ESP32-CAM: Captures image frames and runs AI inference using a quantized YOLOv4-tiny model and Dlib-based facial recognition.

* NodeMCU ESP8266: Manages system logic, plays corresponding audio cues through the DFPlayer Mini, and handles ultrasonic obstacle alerts.

Together, these components deliver multimodal awareness to the user without requiring internet connectivity or bulky hardware. The system was developed with a strong focus on affordability, portability, and real-world usability, and has been validated through both lab testing and pilot user trials.

-----

### File Structure

```

EchoSight/
├── node.cpp                     # NodeMCU firmware (serial + audio + Wi-Fi)
├── esp32_cam.ino                # ESP32-CAM firmware (object + face detection)
├── main.py                      # Python server to receive data from NodeMCU
├── coco.names                   # Class labels for YOLOv4-tiny
├── yolov4-tiny.cfg              # YOLOv4-tiny configuration file
├── yolov4-tiny.weights          # Pretrained YOLOv4-tiny weights
├── Dlib/
│   └── dlib-19.22.0-cp38-cp38-win_amd64.whl   # Offline dlib installer (Windows)
├── images/                      # Put in familiar faces, make sure to name the images with the respective names of the people.
├── audio_files/
├── simpleFaceRecognition.py    # Dlib-based face recognition demo
├── requirements.txt            # Python dependencies for main.py

```
-----

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
**1. Install Arduino IDE**

    * Download and install the Arduino IDE from the official Arduino website [www.arduino.cc](https://www.arduino.cc/en/software).

**2. Install ESP8266 Board Support**

    * Open Arduino IDE.
    
    * Navigate to: `File` → `Preferences`.

In the Additional Board Manager URLs field, add:

```http://arduino.esp8266.com/stable/package_esp8266com_index.json```

   
   * Then go to: `Tools` → `Board` → `Boards Manager`.

   * Search for ESP8266 and click Install.

**3. Connect NodeMCU**

   * Use a Micro USB cable to connect the NodeMCU ESP8266 to your computer.

   * Windows users may need the CH340/CP210x USB drivers, depending on the board’s USB interface.

**4. Select the Board and Port**

   * Go to: Tools → Board → Select NodeMCU 1.0 (ESP-12E Module)

   * Set:

     * Flash Size: 4MB (FS: 1MB OTA: ~1019KB)

     * CPU Frequency: 80 MHz

     * Upload Speed: 115200 baud

   * Go to: `Tools` → `Port` → Choose the COM port corresponding to your NodeMCU.

**5. Wi-Fi and IP Communication: Usage of Server IP**
In `node.cpp`, a variable such as `const char* serverIP = "192.168.X.X"` is defined. This **IP address should be replaced with the IP address of the computer running** the `main.py` server (typically obtained using `ipconfig` on Windows or `ifconfig` on Unix-based systems).

The NodeMCU will send HTTP POST requests to this address at the specified port (e.g., port 5000) whenever it receives a new label or detects an obstacle.

The server (typically using Flask) must be set up to accept incoming requests at the endpoint `/echo`. The Python code parses the JSON payload and either logs or speaks the received message using a text-to-speech engine.

---

### Sensor-to-Audio Feedback Flow
Once both microcontrollers are powered and running:
* **Image Capture and Inference:** The ESP32-CAM captures images at ~5 FPS and processes them locally using YOLOv4-tiny for object detection and Dlib for face recognition.

* **Label Extraction:** If a known object or face is detected with sufficient confidence, the ESP32 generates a descriptive label (e.g., “Car on left”, “John ahead”).

* **Communication:** The label is sent to the NodeMCU via UART (serial communication).

* **Audio Mapping:** The NodeMCU receives the label, looks up the corresponding MP3 index from a predefined table, and sends commands to the DFPlayer Mini.

* **Playback:** The DFPlayer Mini plays the associated MP3 file (e.g., “003.mp3” → “Obstacle on the right”) via speaker or headphone.

* **Ultrasonic Alerts:** Simultaneously, the NodeMCU polls the HC-SR04 sensor every 250 ms. If an object is within a danger threshold (typically 1.5 meters), it overrides the current audio and plays an “obstacle warning” alert.

This ensures real-time, hands-free, and multimodal environmental awareness for the user.

---

### Python-Based Receiver 
For extended capabilities, EchoSight can also transmit sensor data or event logs over Wi-Fi to a Python script running on a PC or Raspberry Pi. The Python file, typically named main.py, acts as a lightweight server that listens on a local IP and port.
**Execution Process:**
1. Ensure that both the NodeMCU and the PC are connected to the same Wi-Fi network.

2. Update the IP and port in the NodeMCU firmware and `main.py` script to match.

3. Install the required Python libraries:

   ```
    pip install -r requirements.txt
   ```
4. Run the script:

   ```
   python main.py
   ```
This script will print incoming messages (e.g., "Obstacle ahead") and can optionally convert them to speech using pyttsx3 or other TTS libraries.

5. Installing Dlib (Offline Fallback)
In systems where `Dlib` fails to install via `pip` due to missing build tools, a precompiled wheel is included in the repository under the Dlib/ directory.

To install manually:

* Ensure you are using Python 3.8 (64-bit), as the wheel is compatible with this version.

* Open a terminal in the root directory of the repository.

* Run:
  ```
  pip install Dlib/dlib-19.22.0-cp38-cp38-win_amd64.whl
  
  ```
Once installed, the face recognition script `simpleFaceRecognition.py` can be run to test known vs. unknown faces using the `images/` directory.

6. Running Face Recognition Standalone (Optional)
The `simpleFaceRecognition.py` script demonstrates how `Dlib` is used to encode known faces and compare them with test images. This can be used to validate that the Dlib module is working correctly.

```
python simpleFaceRecognition.py

```

7. Model Files and Deployment
The following files are required for model inference:

* `yolov4-tiny.cfg`: YOLO configuration

* `yolov4-tiny.weights`: Pretrained weights (~22MB)

* `coco.names`: Class labels used for detection

The ESP32 firmware references these models, which must be converted to TensorFlow Lite format before deployment. This conversion is done offline during training/optimization, and the resulting `.tflite` file is embedded in the ESP32-CAM firmware.

8. Final Execution Flow Summary
Once assembled, flashed, and powered:

* The ESP32-CAM captures frames, runs detection, and sends labels to the NodeMCU.

* The NodeMCU converts those labels to audio commands and plays them.

* The ultrasonic sensor provides redundancy and proximity alerts.

* Optional Wi-Fi communication sends data to a central Python script for monitoring or additional feedback.

* The user receives clear, real-time verbal cues about their environment, improving navigation and safety.

-----

### Project Documentation and Conference Paper

All formal documentation related to the EchoSight project is organized within the `documents/` directory of this repository. This directory includes:

* **Final Project Report:** A comprehensive technical report detailing the system design, hardware-software integration, embedded AI methodologies, evaluation metrics, and user testing. This report serves as the academic deliverable for institutional submission.

* **Conference Paper:** The research paper titled "**EchoSight: An AI-Driven Wearable Device for Assisting the Visually Impaired**" was peer-reviewed and officially accepted for publication and presentation at the **2025 IEEE International Conference on Electronics, Computing and Communication Technologies (CONNECT)**. This paper presents the scientific and engineering contributions of the project, including architectural decisions, embedded inference techniques, sensor fusion, and real-world deployment outcomes.

The paper is copyrighted under **IEEE**, and all rights are reserved. Redistribution or modification of the published paper without appropriate IEEE permission is prohibited. Readers and researchers are encouraged to cite the paper using the official IEEE citation once it becomes available in the conference proceedings.

These documents serve as authoritative references for academic, industrial, or research-based engagements with the EchoSight system.

-----

### License

This repository and all source code (excluding the conference paper) are distributed under the MIT License.

Summary of the MIT License Terms:
 * The software is provided "as is", without any express or implied warranty.

 * Users are permitted to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software.

 * Proper attribution to the original authors must be included in any distributed version or derivative work.

 * The complete license text is available in the `LICENSE` file located at the root of this repository.

Please note that while the project code is open-source under MIT terms, the conference paper remains copyrighted under **IEEE**.





