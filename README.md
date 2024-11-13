


# Robot Interaction System

This project provides a framework for a robot to interact with users through speech recognition, audio processing, and visual object detection. The robot responds to specific commands, recognizes objects by color, and performs basic actions.

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Functionality Overview](#functionality-overview)
- [Troubleshooting](#troubleshooting)

## Project Structure

The project includes two main files:

- **`robot.py`**: Implements the robot's interaction logic.
  - Handles speech recognition with pre-set phrases that trigger responses or actions.
  - Includes audio recording and color-based object recognition.
  - Uses predefined responses stored in an external `dictionary.txt` file.
  - Controls robot movements and actions like standing, sitting, walking, and object manipulation.

- **`connector.py`**: Manages the robot’s network connection and authentication.
  - Establishes a secure connection to the robot through an IP address and port.
  - Implements a custom `Authenticator` class to authenticate the robot's API.

## Requirements

- **Python 3.x**
- **Python Libraries**:
  - `qi` (robot-specific)
  - `paramiko`
  - `scp`
  - `speech_recognition`
  - `opencv-python-headless`
  - `soundfile`
  - `numpy`
- **NAO Robot Software (if applicable)**: Follow NAO API documentation for robot libraries.

## Installation

1. **Install Required Libraries**:

    ```bash
    pip install paramiko scp speechrecognition opencv-python-headless soundfile numpy
    ```

2. **Install NAO Libraries**:

   If working with a NAO robot, install specific libraries for `qi` and other robot control tools as per the [NAO API documentation](https://www.softbankrobotics.com/emea/en/nao).

## Configuration

1. **Update Connection Details**:
   - In `connector.py`, replace `"IP_ADDRESS"` and `"PORT"` with your robot's IP address and connection port.
   - In `robot.py`, update `"username"` and `"password"` for secure SSH connection.

2. **Add Dictionary File**:
   - Create a `dictionary.txt` file at the project root.
   - Format each entry as follows:
     
     ```txt
     "keyword"={"response1", "response2"}
     ```

   - Example:
     
     ```txt
     "hello"={"Hi there!", "Hello!"}
     ```

## Usage

1. **Run the Robot Interaction Program**:

    ```bash
    python robot.py
    ```

2. **Commands and Features**:
   - **Speech Commands**: Recognizes commands like `"hello"`, `"what's your name"`, `"stand"`, `"sit"`, and `"goodbye"`.
   - **Object Detection**: Detects objects by color (e.g., red or green balls) using the camera.
   - **Audio Recording**: Records audio when spoken to, processes it, and responds based on recognized commands.

## Functionality Overview

- **robot.py**
  - **Basic Actions**: Commands for `stand_position` and `sit_position` adjust the robot’s posture.
  - **Audio Recording and Recognition**:
    - `listen()`: Records audio for 5 seconds.
    - `detect_speech()`: Processes the recorded audio file for speech recognition.
  - **Object Detection**: Detects objects by color using the camera, marking them with bounding boxes.
  - **Response Handling**: Uses predefined phrases from the dictionary to respond based on recognized commands.

- **connector.py**
  - **Connection Management**: Sets up a secure connection with the robot.
  - **Authenticator Class**: Provides login details for robot API authentication.

## Troubleshooting

If the robot does not respond:

- Verify that the `dictionary.txt` file is correctly formatted.
- Ensure the IP address, username, and password in `connector.py` are accurate.
- Confirm that all dependencies are installed and the `qi` library is accessible.

---

