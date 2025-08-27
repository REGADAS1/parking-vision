# Parking Vision – Real-Time Parking Spot Detection (Python + OpenCV)

This project is a real-time parking occupancy detection system built in Python using OpenCV. A mobile phone acts as a camera (via IP Webcam or similar apps) streaming live video to a PC. The software then processes the video feed and determines whether each parking spot is free or occupied.

The system allows you to:

Define multiple parking spots manually (rectangles drawn on live video).

Capture a baseline image of empty spots for accurate comparison.

Detect vehicles using a combination of edge analysis and shadow-robust background subtraction.

Display each parking spot with green (free) or red (occupied) bounding boxes.

Handle real-world conditions like shadows, brightness changes, and small camera movements.

Update the baseline dynamically when spots remain free for a while.

Exit gracefully when pressing q or closing the video window.

This tool can serve as a proof-of-concept for smart parking systems and be expanded into enterprise solutions with cloud integration, license plate recognition, or IoT hardware.

---

Parking Vision is a computer vision project that detects whether parking spots are free or occupied using live video from a mobile phone or webcam.  
The system is built with Python + OpenCV, supports manual calibration, and is robust against shadows and camera shakes.

---

## Features
- Use a mobile phone (IP Webcam app) or webcam as a video source.
- Define parking spots manually by drawing rectangles.
- Green = Free | Red = Occupied
- Robust against shadows, brightness changes, and small camera movement.
- Adaptive baseline update when spots stay free for a while.
- Keyboard shortcuts for quick control:
  - `q` → Quit
  - `b` → Update baseline
  - `s` → Save screenshot
- Closing the window also safely stops the application.

---

## Project Structure
```
parking_vision/
│── data/                   # ROI (spots) and baseline image are stored here
│── src/
│   ├── run.py              # Main real-time detection script
│   ├── calibrate_rois.py   # Tool to manually define parking spots
│   ├── capture_baseline.py # Capture baseline with all spots free
│   ├── config.py           # Configuration and thresholds
│   ├── utils.py            # Helper functions (drawing, video capture, etc.)
│   └── detectors/          # Detection methods (edge, diff, hybrid)
│── requirements.txt        # Python dependencies
│── README.md               # Project documentation
```

---

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/parking-vision.git
   cd parking-vision
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### 1. Calibrate parking spots
Run once to draw rectangles around each parking spot (live video window will appear):
```bash
python -m src.calibrate_rois --source "http://PHONE_IP:8080/video"
```
or with webcam:
```bash
python -m src.calibrate_rois --source 0
```

### 2. Capture baseline (all spots empty)
```bash
python -m src.capture_baseline --source "http://PHONE_IP:8080/video"
```

### 3. Run detection in real-time
```bash
python -m src.run --source "http://PHONE_IP:8080/video"
```

---

## Requirements
- Python 3.9+
- Packages:
  - opencv-python
  - numpy

Install via:
```bash
pip install -r requirements.txt
```

---

## How It Works
1. Baseline Image: A snapshot is stored when all spots are empty.
2. Detection: Each frame is compared against the baseline using:
   - Edge density (canny contours).
   - Shadow-robust background subtraction in HSV color space.
3. Decision: If a spot shows significant difference or edge density, it is marked OCCUPIED.
4. Adaptive Reset: If a spot stays free for a while, its baseline is refreshed to account for lighting changes.

---

## Future Improvements
- License plate recognition (ANPR).
- Cloud dashboard integration (Flask/Django + database).
- IoT integration with parking sensors and gates.
- Mobile app for drivers to check available spots.

---

## License
This project is licensed under the MIT License – feel free to use and modify it.
