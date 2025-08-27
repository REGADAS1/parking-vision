from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)

ROIS_PATH = DATA_DIR / "rois.json"
BASELINE_PATH = DATA_DIR / "baseline.jpg"

DEFAULT_PARAMS = {
    "edge": {
        "canny1": 60,
        "canny2": 180,
        "edge_margin": 0.015
    },
    "diff": {
        "diff_threshold": 25,
        "diff_ratio_threshold": 0.020
    },
    "smooth": {
        "frames_to_confirm": 3
    },
    "display": {
        "show_labels": True,
        "font_scale": 0.7,
        "thickness": 2
    }
}

def save_rois(rois: list):
    """Save ROIs to a JSON file."""
    with open(ROIS_PATH, "w", encoding="utf-8") as f:
        json.dump(rois, f, ensure_ascii=False, indent=2)

def load_rois():
    """Load ROIs from a JSON file."""
    if not ROIS_PATH.exists():
        raise FileNotFoundError(f"ROI file not found: {ROIS_PATH}")
    with open(ROIS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
