import cv2
import numpy as np

def diff_ratio(gray_roi, gray_roi_baseline, diff_threshold=25):
    d = cv2.absdiff(gray_roi, gray_roi_baseline)
    _, th = cv2.threshold(d, diff_threshold, 255, cv2.THRESH_BINARY)
    th = cv2.medianBlur(th, 3)
    total = gray_roi.shape[0] * gray_roi.shape[1]
    cnt = cv2.countNonZero(th)
    return cnt / max(1, total)