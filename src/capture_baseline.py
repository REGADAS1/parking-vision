import argparse
import cv2
from .utils import open_capture
from .config import DATA_DIR, BASELINE_PATH

def main():
    parser = argparse.ArgumentParser(description="Capture baseline with empty parking spots.")
    parser.add_argument("--source", required=True, help="0 (webcam) or URL")
    args = parser.parse_args()

    cap = open_capture(args.source)
    print("Capturing baseline in 2 seconds. Make sure all spots are free.")
    cv2.waitKey(2000)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError("Could not capture baseline.")

    DATA_DIR.mkdir(exist_ok=True, parents=True)
    cv2.imwrite(str(BASELINE_PATH), frame)
    print(f"Baseline saved to {BASELINE_PATH}.")

if __name__ == "__main__":
    main()
