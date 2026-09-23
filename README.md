# TrackingHand

A computer vision hand gesture tracking tool built with Python, OpenCV, and MediaPipe, featuring real-time motion capture streaming to Roblox Studio.

TrackingHand captures webcam video, detects 21 hand landmarks in 3D coordinates, and translates finger flexions and wrist orientations into control signals for desktop navigation and Roblox models.

## Features

- **MediaPipe Landmark Tracking**: Tracks 21 3D joint positions per hand with low latency on standard webcams.
- **Roblox Studio Integration**: Streams rotational joint data to a bionic hand model inside Roblox Studio via local HTTP polling (~7 requests/second to respect HttpService quotas).
- **Desktop Gesture Mapping**: Optional mouse cursor steering, left/right clicks, and scrolling triggered by thumb and finger pinches.
- **Decoupled Thumb Kinematics**: Calibrated Carpometacarpal (CMC), Metacarpophalangeal (MCP), and Interphalangeal (IP) calculations to prevent thumb flexion from distorting spread angles.

## Installation

### Prerequisites

- Windows 10/11
- Python 3.10 or higher
- Webcam

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/IlhamXkyo/TrackingHand.git
   cd TrackingHand
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Run Tracker
Start the Python tracking server:
```bash
python hand_tracker.py
```

### 2. Connect to Roblox Studio
1. Open the Roblox place containing the bionic hand rig.
2. Ensure **HttpService** is enabled in Game Settings (Home > Game Settings > Options > Allow HTTP Requests).
3. Press **Play** or **Run** (F8) in Roblox Studio. The rig will mirror your hand movements in real-time.

## Tech Stack

- Python 3.10+
- MediaPipe
- OpenCV
- PyDirectInput
- Roblox Luau

## License

MIT License. See LICENSE for details.
