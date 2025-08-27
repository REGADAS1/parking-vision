import cv2
import numpy as np

def edge_ratio(gray_roi, canny1=60, canny2=180):
    blur = cv2.GaussianBlur(gray_roi, (5, 5), 0)
    edges = cv2.Canny(blur, canny1, canny2)
    edges = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
    total = gray_roi.shape[0] * gray_roi.shape[1]
    cnt = cv2.countNonZero(edges)
    return cnt / max(1, total)