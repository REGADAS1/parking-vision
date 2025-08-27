import argparse
from pathlib import Path
import cv2
import numpy as np

from .config import load_rois, BASELINE_PATH, DATA_DIR, DEFAULT_PARAMS
from .utils import open_capture, draw_labelled_box, save_screenshot, Debouncer, GREEN, RED, WHITE
from .detectors.edge_based import edge_ratio as compute_edge_ratio

# -------------------- ROBUSTNESS PARAMETERS --------------------
OCCUPY_FRAMES = 6      # consecutive frames to confirm OCCUPIED
FREE_FRAMES   = 3      # consecutive frames to confirm FREE
MIN_AREA      = 0.04   # min % of changed area required to count as occupied
CLEAR_THRESH  = 0.012  # if diff < 1.2% during FREE_FRAMES => local baseline reset

# -------------------- HELPERS --------------------
def fit_to_screen(image, max_w=1600, max_h=900):
    """Resize the image to fit on screen without cropping."""
    h, w = image.shape[:2]
    scale = min(max_w / w, max_h / h, 1.0)
    if scale < 1.0:
        image = cv2.resize(image, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
    return image

def align_to_baseline(gray_frame, gray_baseline,
                      warp_mode=cv2.MOTION_EUCLIDEAN,
                      number_of_iterations=30, termination_eps=1e-3):
    """Aligns the current frame to the baseline to reduce impact of small camera shifts."""
    warp_matrix = np.eye(2, 3, dtype=np.float32)
    try:
        criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                    number_of_iterations, termination_eps)
        _, warp_matrix = cv2.findTransformECC(
            gray_baseline, gray_frame, warp_matrix, warp_mode, criteria, None, 5
        )
        aligned = cv2.warpAffine(
            gray_frame, warp_matrix, (gray_frame.shape[1], gray_frame.shape[0]),
            flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE
        )
        return aligned
    except cv2.error:
        return gray_frame  # fallback

def compute_edge_baselines(baseline_gray, rois, canny1, canny2):
    baselines = []
    for r in rois:
        x, y, w, h = r["x"], r["y"], r["w"], r["h"]
        crop = baseline_gray[y:y+h, x:x+w]
        er = compute_edge_ratio(crop, canny1, canny2)
        baselines.append(er)
    return baselines

# -------------------- MAIN PROGRAM --------------------
def main():
    parser = argparse.ArgumentParser(description="Parking spot occupancy detection (real-time).")
    parser.add_argument("--source", required=True, help="0 (webcam) or URL (RTSP/MJPEG/HTTP)")
    parser.add_argument("--show_labels", type=int, default=1)
    args = parser.parse_args()

    rois = load_rois()
    cap = open_capture(args.source)

    ok, frame = cap.read()
    if not ok:
        raise RuntimeError("Could not read initial frame from video source.")

    if BASELINE_PATH.exists():
        baseline_bgr = cv2.imread(str(BASELINE_PATH), cv2.IMREAD_COLOR)
        if baseline_bgr is None:
            print("Warning: baseline.jpg invalid. Using current frame as baseline.")
            baseline_bgr = frame.copy()
    else:
        print("Warning: baseline.jpg not found. Using current frame as baseline.")
        baseline_bgr = frame.copy()

    baseline_gray = cv2.cvtColor(baseline_bgr, cv2.COLOR_BGR2GRAY)

    canny1 = DEFAULT_PARAMS["edge"]["canny1"]
    canny2 = DEFAULT_PARAMS["edge"]["canny2"]
    edge_margin = DEFAULT_PARAMS["edge"]["edge_margin"]
    diff_ratio_threshold = 0.03  # less sensitive to shadows
    show_labels = bool(args.show_labels)

    edge_baselines = compute_edge_baselines(baseline_gray, rois, canny1, canny2)
    debouncers = {r["id"]: Debouncer(initial_state=False, frames_to_confirm=1) for r in rois}
    free_streak = {r["id"]: 0 for r in rois}
    occ_streak  = {r["id"]: 0 for r in rois}

    win_name = "Parking Vision - Real Time"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, 1280, 720)

    print("Running. Keys: [q]=quit, [b]=update baseline, [s]=screenshot")
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Video read failed. Exiting...")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_aligned = align_to_baseline(gray, baseline_gray)

        free_flags = []
        for idx, r in enumerate(rois):
            rid, name = r["id"], r["name"]
            x, y, w, h = r["x"], r["y"], r["w"], r["h"]

            roi_gray = gray_aligned[y:y+h, x:x+w]
            roi_bgr  = frame[y:y+h, x:x+w]
            base_bgr = baseline_bgr[y:y+h, x:x+w]

            # Shadow-robust difference (HSV)
            roi_hsv, base_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV), cv2.cvtColor(base_bgr, cv2.COLOR_BGR2HSV)
            roi_v, base_v = cv2.equalizeHist(roi_hsv[:,:,2]), cv2.equalizeHist(base_hsv[:,:,2])
            dh = cv2.absdiff(roi_hsv[:,:,0], base_hsv[:,:,0])
            ds = cv2.absdiff(roi_hsv[:,:,1], base_hsv[:,:,1])
            dv = cv2.absdiff(roi_v, base_v)
            mix = cv2.addWeighted(dh, 0.45, ds, 0.45, 0)
            mix = cv2.addWeighted(mix, 1.0, dv, 0.10, 0)
            _, th = cv2.threshold(mix, 20, 255, cv2.THRESH_BINARY)
            th = cv2.medianBlur(th, 3)
            diff_ratio = cv2.countNonZero(th) / max(1, th.size)

            # Edge feature
            er = compute_edge_ratio(roi_gray, canny1, canny2)

            # Raw decision
            occupied_diff = (diff_ratio > diff_ratio_threshold) and (diff_ratio > MIN_AREA)
            occupied_edge = er > (edge_baselines[idx] + edge_margin)
            occupied_now = bool(occupied_diff or occupied_edge)

            # Asymmetric hysteresis
            if occupied_now:
                occ_streak[rid] += 1
                free_streak[rid] = 0
            else:
                free_streak[rid] += 1
                occ_streak[rid] = 0

            if occ_streak[rid] >= OCCUPY_FRAMES:
                state = True
            elif free_streak[rid] >= FREE_FRAMES and diff_ratio < CLEAR_THRESH:
                state = False
            else:
                state = debouncers[rid].state

            debouncers[rid].state = state
            color = RED if state else GREEN
            free_flags.append(not state)

            # Local baseline reset when consistently free
            if not state and free_streak[rid] == FREE_FRAMES and diff_ratio < CLEAR_THRESH:
                baseline_gray[y:y+h, x:x+w] = gray_aligned[y:y+h, x:x+w]
                baseline_bgr[y:y+h, x:x+w]  = frame[y:y+h, x:x+w]
                edge_baselines[idx] = compute_edge_ratio(baseline_gray[y:y+h, x:x+w], canny1, canny2)

            # Draw box
            label = None
            if show_labels:
                status = "OCCUPIED" if state else "FREE"
                label = f"{name}: {status}"
            draw_labelled_box(frame, x, y, w, h, color, label=label,
                              font_scale=DEFAULT_PARAMS["display"]["font_scale"],
                              thickness=DEFAULT_PARAMS["display"]["thickness"])

        # Header
        free_count = sum(free_flags)
        header = f"Free spots: {free_count}/{len(rois)}"
        cv2.putText(frame, header, (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.9, WHITE, 2, cv2.LINE_AA)

        # Show (fit-to-screen)
        view = fit_to_screen(frame, max_w=1600, max_h=900)
        cv2.imshow(win_name, view)

        # Exit if window closed
        if cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE) < 1:
            break

        # Key commands
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('b'):
            baseline_gray = gray.copy()
            baseline_bgr = frame.copy()
            edge_baselines = compute_edge_baselines(baseline_gray, rois, canny1, canny2)
            print("Baseline updated from current frame.")
        elif key == ord('s'):
            path = save_screenshot(frame, Path("data"))
            print(f"Screenshot saved to: {path}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
