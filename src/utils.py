import cv2
import time
from pathlib import Path

GREEN  = (0, 255, 0)
RED    = (0, 0, 255)
YELLOW = (0, 255, 255)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)

def open_capture(source: str):
    import cv2, re, time
    # Local webcam (0/1/2…)
    if isinstance(source, str) and source.isdigit():
        cap = cv2.VideoCapture(int(source))
        if not cap.isOpened():
            raise RuntimeError(f"Could not open webcam: {source}")
        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
        return cap

    # HTTP/RTSP streams: try several known endpoints with FFMPEG
    candidates = [source]
    if re.match(r"^https?://[\d\.]+:\d+/?$", source):
        base = source.rstrip("/")
        candidates += [
            f"{base}/video",
            f"{base}/stream.mjpg",
            f"{base}/videofeed",
            f"{base}/mjpegfeed"
        ]
    elif source.endswith("/"):
        candidates += [
            source + "video",
            source + "stream.mjpg",
            source + "videofeed",
            source + "mjpegfeed"
        ]

    last_err = None
    for url in candidates:
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        if cap.isOpened():
            # try reading 1–2 frames to validate
            ok, _ = cap.read()
            if ok:
                try:
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                except Exception:
                    pass
                return cap
            cap.release()
        last_err = url
        time.sleep(0.2)
    raise RuntimeError(f"Could not open video source. Tested: {candidates}")


def draw_labelled_box(img, x, y, w, h, color, label=None, font_scale=0.7, thickness=2):
    """Draw a rectangle with an optional label above it."""
    cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
    if label:
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        cv2.rectangle(img, (x, y - th - 8), (x + tw + 6, y), color, -1)
        cv2.putText(img, label, (x + 3, y - 6), cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale, (0,0,0), thickness, cv2.LINE_AA)

def save_screenshot(img, out_dir: Path):
    """Save a screenshot of the current frame into the output directory."""
    out_dir.mkdir(exist_ok=True, parents=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"frame_{ts}.jpg"
    cv2.imwrite(str(path), img)
    return path

class Debouncer:
    """Ensures that state changes are only confirmed after N consecutive frames."""
    def __init__(self, initial_state: bool, frames_to_confirm: int = 3):
        self.state = initial_state
        self.pending_state = initial_state
        self.counter = 0
        self.frames_to_confirm = frames_to_confirm

    def update(self, new_state: bool):
        if new_state == self.state:
            self.pending_state = new_state
            self.counter = 0
            return self.state
        if new_state == self.pending_state:
            self.counter += 1
        else:
            self.pending_state = new_state
            self.counter = 1
        if self.counter >= self.frames_to_confirm:
            self.state = self.pending_state
            self.counter = 0
        return self.state
