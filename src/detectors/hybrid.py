from .edge_based import edge_ratio as _edge_ratio
from .background_diff import diff_ratio as _diff_ratio

def decide_occupied(gray_roi, gray_roi_baseline, *,
                    canny1, canny2, edge_baseline, edge_margin,
                    diff_threshold, diff_ratio_threshold):
    er = _edge_ratio(gray_roi, canny1, canny2)
    dr = _diff_ratio(gray_roi, gray_roi_baseline, diff_threshold)
    occupied_edge = er > (edge_baseline + edge_margin)
    occupied_diff = dr > diff_ratio_threshold
    return bool(occupied_edge or occupied_diff), er, dr