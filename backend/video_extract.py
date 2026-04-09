"""
Video frame extraction utilities.
"""

import cv2
import numpy as np
from pathlib import Path


def extract_all_frames(video_path: str, target_fps: float = 10.0) -> list[np.ndarray]:
    """
    Extract frames from a video at a target FPS rate.
    Returns list of BGR numpy arrays.
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    source_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_interval = max(1, int(source_fps / target_fps))
    frames = []
    idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % frame_interval == 0:
            frames.append(frame)
        idx += 1

    cap.release()
    return frames


def get_video_info(video_path: str) -> dict:
    """Get basic video metadata."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    info = {
        "fps": cap.get(cv2.CAP_PROP_FPS),
        "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    }
    info["duration"] = info["frame_count"] / info["fps"] if info["fps"] > 0 else 0
    cap.release()
    return info


def extract_frame_at_index(video_path: str, frame_index: int) -> np.ndarray | None:
    """Extract a single frame at a specific index."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    cap.release()
    return frame if ret else None


def save_frame(frame: np.ndarray, output_path: str, quality: int = 95) -> str:
    """Save a frame as JPEG. Returns the output path."""
    cv2.imwrite(str(output_path), frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return str(output_path)


def generate_thumbnail(frame: np.ndarray, max_width: int = 200) -> np.ndarray:
    """Resize frame to thumbnail size."""
    h, w = frame.shape[:2]
    scale = max_width / w
    new_w = max_width
    new_h = int(h * scale)
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
