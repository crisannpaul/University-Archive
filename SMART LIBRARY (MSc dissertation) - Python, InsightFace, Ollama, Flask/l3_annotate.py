"""OpenCV bbox + label drawing for caption frames.

Spec reference: "Caption op detail → step 3" + Configuration knobs
`CAPTION_ANNOTATE_BOX_COLOR`, `CAPTION_ANNOTATE_LABEL_FONT_SCALE`.

Only detections with `matched_name != null` are drawn. Anonymous detections
are intentionally not annotated — the caption prompt's "do not guess names"
rule depends on unlabelled faces staying generic ("a man", "a group") in the
VLM's prose.
"""

from __future__ import annotations

import cv2
import numpy as np

import l1_config as config

_FONT = cv2.FONT_HERSHEY_SIMPLEX
_BOX_THICKNESS = 2
_TEXT_THICKNESS = 2
_TEXT_PAD = 4  # pixels around the label inside its background pill


def draw_named_detections(frame: np.ndarray, detections: list[dict]) -> np.ndarray:
    """Return a copy of `frame` with bbox + name labels for matched detections.

    Each detection follows the spec's `.faces.json` shape:
    `{"frame_t_s": ..., "bbox": [x, y, w, h], "matched_name": str | None, ...}`.
    Detections with `matched_name=None` are skipped.
    """
    if not detections:
        return frame

    out = frame.copy()
    color = tuple(int(c) for c in config.CAPTION_ANNOTATE_BOX_COLOR)  # BGR
    font_scale = float(config.CAPTION_ANNOTATE_LABEL_FONT_SCALE)
    h_img, w_img = out.shape[:2]

    for d in detections:
        name = d.get("matched_name")
        if not name:
            continue
        bbox = d.get("bbox")
        if not bbox or len(bbox) != 4:
            continue
        x, y, w, h = bbox
        x1 = max(0, int(round(x)))
        y1 = max(0, int(round(y)))
        x2 = min(w_img - 1, int(round(x + w)))
        y2 = min(h_img - 1, int(round(y + h)))
        if x2 <= x1 or y2 <= y1:
            continue

        cv2.rectangle(out, (x1, y1), (x2, y2), color, _BOX_THICKNESS)

        label = str(name)
        (tw, th), baseline = cv2.getTextSize(label, _FONT, font_scale, _TEXT_THICKNESS)
        # Solid pill above the bbox top-left; flip below the box if it'd clip.
        bg_top = y1 - th - _TEXT_PAD - baseline
        if bg_top < 0:
            bg_top = y2
            text_baseline = y2 + th + _TEXT_PAD
        else:
            text_baseline = y1 - _TEXT_PAD
        bg_bottom = bg_top + th + _TEXT_PAD + baseline
        bg_right = min(w_img - 1, x1 + tw + _TEXT_PAD * 2)
        cv2.rectangle(out, (x1, bg_top), (bg_right, bg_bottom), color, -1)
        cv2.putText(
            out, label, (x1 + _TEXT_PAD, text_baseline),
            _FONT, font_scale, (0, 0, 0), _TEXT_THICKNESS, lineType=cv2.LINE_AA,
        )

    return out
