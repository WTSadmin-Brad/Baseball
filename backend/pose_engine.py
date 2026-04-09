"""
Pose detection and swing metrics engine.
Refactored from swing_analysis.py for use as a library.
"""

import math
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
from pathlib import Path

# ── Model path ───────────────────────────────────────────────────────────────
MODEL_PATH = Path(__file__).resolve().parent.parent / "pose_landmarker_heavy.task"

# ── Swing phase labels ───────────────────────────────────────────────────────
SWING_PHASES = [
    "Stance / Setup",
    "Early Load",
    "Load / Stride",
    "Launch Position",
    "Swing Initiation",
    "Connection / Approach",
    "Contact / Extension",
    "Follow-Through / Finish",
]

# ── Landmark indices (MediaPipe Pose) ────────────────────────────────────────
LANDMARK_NAMES = {
    0: "nose", 1: "left_eye_inner", 2: "left_eye", 3: "left_eye_outer",
    4: "right_eye_inner", 5: "right_eye", 6: "right_eye_outer",
    7: "left_ear", 8: "right_ear", 9: "mouth_left", 10: "mouth_right",
    11: "left_shoulder", 12: "right_shoulder",
    13: "left_elbow", 14: "right_elbow",
    15: "left_wrist", 16: "right_wrist",
    17: "left_pinky", 18: "right_pinky",
    19: "left_index", 20: "right_index",
    21: "left_thumb", 22: "right_thumb",
    23: "left_hip", 24: "right_hip",
    25: "left_knee", 26: "right_knee",
    27: "left_ankle", 28: "right_ankle",
    29: "left_heel", 30: "right_heel",
    31: "left_foot_index", 32: "right_foot_index",
}

# Key landmarks used for swing analysis
SWING_LANDMARKS = [
    0, 7, 8,        # nose, ears
    11, 12,          # shoulders
    13, 14,          # elbows
    15, 16,          # wrists
    19, 20,          # index fingers
    23, 24,          # hips
    25, 26,          # knees
    27, 28,          # ankles
]

# Skeletal connections for drawing lines
SKELETON_CONNECTIONS = [
    # Shoulder line
    (11, 12, "shoulder"),
    # Hip line
    (23, 24, "hip"),
    # Front arm (left = front for RH batter)
    (11, 13, "front_arm"), (13, 15, "front_arm"),
    # Back arm
    (12, 14, "back_arm"), (14, 16, "back_arm"),
    # Front leg
    (23, 25, "front_leg"), (25, 27, "front_leg"),
    # Back leg
    (24, 26, "back_leg"), (26, 28, "back_leg"),
    # Wrist-to-wrist (bat approximation)
    (15, 16, "bat"),
    # Wrist to index (bat direction)
    (15, 19, "bat"), (16, 20, "bat"),
]

# Color palette (RGB for frontend, will convert to BGR for OpenCV)
COLORS_RGB = {
    "hip":       (255, 100, 0),
    "shoulder":  (0, 200, 255),
    "spine":     (255, 255, 255),
    "front_arm": (100, 255, 0),
    "back_arm":  (0, 255, 100),
    "front_leg": (255, 230, 0),
    "back_leg":  (230, 200, 0),
    "head":      (255, 255, 255),
    "bat":       (255, 180, 0),
    "plumb":     (200, 200, 200),
}


# ── Math utilities ───────────────────────────────────────────────────────────

def angle_between_points(a, b, c):
    """Angle at point b formed by line segments ba and bc, in degrees."""
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    return float(math.degrees(math.acos(np.clip(cos_angle, -1.0, 1.0))))


def line_angle_from_horizontal(p1, p2):
    """Angle of line p1→p2 relative to horizontal, in degrees."""
    dx = p2[0] - p1[0]
    dy = -(p2[1] - p1[1])  # Invert y (image coords)
    return float(math.degrees(math.atan2(dy, dx)))


def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


# ── Pose detection ───────────────────────────────────────────────────────────

def detect_landmarks(image_path: str) -> list[dict] | None:
    """
    Run MediaPipe pose detection on an image.
    Returns list of 33 landmark dicts: {x, y, z, visibility, name}
    Coordinates are normalized [0,1].
    """
    img = cv2.imread(str(image_path))
    if img is None:
        return None

    options = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
    )
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
        )
        results = landmarker.detect(mp_image)

    if not results.pose_landmarks or len(results.pose_landmarks) == 0:
        return None

    landmarks = []
    for i, lm in enumerate(results.pose_landmarks[0]):
        landmarks.append({
            "id": i,
            "name": LANDMARK_NAMES.get(i, f"landmark_{i}"),
            "x": float(lm.x),
            "y": float(lm.y),
            "z": float(lm.z),
            "visibility": float(lm.visibility) if lm.visibility else 0.0,
        })
    return landmarks


def compute_metrics(landmarks: list[dict], image_width: int, image_height: int) -> dict:
    """
    Compute swing analysis metrics from landmark positions.
    Landmarks should have normalized x,y coords.
    Returns dict of metric name → value.
    """
    def px(idx):
        lm = landmarks[idx]
        if lm["visibility"] < 0.15:
            return None
        return (lm["x"] * image_width, lm["y"] * image_height)

    metrics = {}

    # Shoulder and hip points
    l_shoulder = px(11)
    r_shoulder = px(12)
    l_hip = px(23)
    r_hip = px(24)

    # Hip-shoulder rotation
    if l_hip and r_hip:
        metrics["hip_line_angle"] = line_angle_from_horizontal(l_hip, r_hip)
    if l_shoulder and r_shoulder:
        metrics["shoulder_line_angle"] = line_angle_from_horizontal(l_shoulder, r_shoulder)
    if "hip_line_angle" in metrics and "shoulder_line_angle" in metrics:
        raw_diff = metrics["shoulder_line_angle"] - metrics["hip_line_angle"]
        metrics["hip_shoulder_separation"] = abs((raw_diff + 180) % 360 - 180)

    # Back elbow angle
    if r_shoulder and px(14) and px(16):
        metrics["back_elbow_angle"] = angle_between_points(r_shoulder, px(14), px(16))

    # Front elbow angle
    if l_shoulder and px(13) and px(15):
        metrics["front_elbow_angle"] = angle_between_points(l_shoulder, px(13), px(15))

    # Front knee angle
    if l_hip and px(25) and px(27):
        metrics["front_knee_angle"] = angle_between_points(l_hip, px(25), px(27))

    # Back knee angle
    if r_hip and px(26) and px(28):
        metrics["back_knee_angle"] = angle_between_points(r_hip, px(26), px(28))

    # Spine tilt (from vertical)
    if l_shoulder and r_shoulder and l_hip and r_hip:
        mid_s = midpoint(l_shoulder, r_shoulder)
        mid_h = midpoint(l_hip, r_hip)
        dx = mid_s[0] - mid_h[0]
        dy = mid_s[1] - mid_h[1]
        metrics["spine_tilt"] = float(math.degrees(math.atan2(abs(dx), abs(dy))))

    return metrics


def render_annotated_frame(
    image_path: str,
    landmarks: list[dict],
    metrics: dict,
    phase_label: str,
) -> np.ndarray:
    """
    Render an annotated frame with skeleton overlay, markers, and metrics.
    Returns the annotated image as a numpy array (BGR).
    """
    img = cv2.imread(str(image_path))
    if img is None:
        raise FileNotFoundError(f"Cannot read {image_path}")

    h, w = img.shape[:2]
    marker_r = max(4, int(w * 0.008))
    line_thick = max(2, int(w * 0.004))
    thin_thick = max(1, int(w * 0.002))
    font_scale = max(0.35, w / 1800)

    def px(idx):
        lm = landmarks[idx]
        if lm["visibility"] < 0.15:
            return None
        return (int(lm["x"] * w), int(lm["y"] * h))

    def bgr(rgb):
        return (rgb[2], rgb[1], rgb[0])

    overlay = img.copy()

    # Draw skeleton lines
    for idx_a, idx_b, group in SKELETON_CONNECTIONS:
        pa, pb = px(idx_a), px(idx_b)
        if pa and pb:
            color = bgr(COLORS_RGB.get(group, (200, 200, 200)))
            cv2.line(overlay, pa, pb, color, line_thick, cv2.LINE_AA)

    # Spine line
    l_s, r_s = px(11), px(12)
    l_h, r_h = px(23), px(24)
    if l_s and r_s and l_h and r_h:
        mid_s = (int((l_s[0]+r_s[0])/2), int((l_s[1]+r_s[1])/2))
        mid_h = (int((l_h[0]+r_h[0])/2), int((l_h[1]+r_h[1])/2))
        cv2.line(overlay, mid_s, mid_h, bgr(COLORS_RGB["spine"]), line_thick, cv2.LINE_AA)

    # Head → mid-shoulder
    nose = px(0)
    if nose and l_s and r_s:
        mid_s = (int((l_s[0]+r_s[0])/2), int((l_s[1]+r_s[1])/2))
        cv2.line(overlay, nose, mid_s, bgr(COLORS_RGB["head"]), thin_thick, cv2.LINE_AA)

    # Plumb line from nose
    if nose:
        cv2.line(overlay, (nose[0], 0), (nose[0], h), bgr(COLORS_RGB["plumb"]), thin_thick, cv2.LINE_AA)

    # Rotation extension lines
    extend = int(w * 0.06)
    for pa_idx, pb_idx, group in [(23, 24, "hip"), (11, 12, "shoulder")]:
        pa, pb = px(pa_idx), px(pb_idx)
        if pa and pb:
            dx, dy = pb[0]-pa[0], pb[1]-pa[1]
            length = math.sqrt(dx*dx + dy*dy) + 1e-8
            ux, uy = dx/length, dy/length
            ext_a = (int(pa[0] - ux*extend), int(pa[1] - uy*extend))
            ext_b = (int(pb[0] + ux*extend), int(pb[1] + uy*extend))
            color = bgr(COLORS_RGB[group])
            cv2.line(overlay, ext_a, pa, color, thin_thick, cv2.LINE_AA)
            cv2.line(overlay, pb, ext_b, color, thin_thick, cv2.LINE_AA)

    # Blend overlay
    img = cv2.addWeighted(overlay, 0.85, img, 0.15, 0)

    # Draw joint markers
    joint_groups = {
        0: "head", 7: "head", 8: "head",
        11: "shoulder", 12: "shoulder",
        13: "front_arm", 14: "back_arm",
        15: "front_arm", 16: "back_arm",
        23: "hip", 24: "hip",
        25: "front_leg", 26: "back_leg",
        27: "front_leg", 28: "back_leg",
    }
    for idx, group in joint_groups.items():
        pt = px(idx)
        if pt:
            color = bgr(COLORS_RGB.get(group, (200, 200, 200)))
            cv2.circle(img, pt, marker_r, color, -1, cv2.LINE_AA)
            cv2.circle(img, pt, marker_r, (255, 255, 255), 1, cv2.LINE_AA)

    # Metrics panel (top-right)
    panel_w = int(w * 0.48)
    line_h = max(16, int(font_scale * 30))
    lines = [f"PHASE: {phase_label}", "---"]
    metric_labels = [
        ("hip_line_angle", "Hip Rotation"),
        ("shoulder_line_angle", "Shoulder Rotation"),
        ("hip_shoulder_separation", "Hip-Shoulder Sep"),
        ("back_elbow_angle", "Back Elbow"),
        ("front_elbow_angle", "Front Elbow"),
        ("front_knee_angle", "Front Knee"),
        ("back_knee_angle", "Back Knee"),
        ("spine_tilt", "Spine Tilt"),
    ]
    for key, label in metric_labels:
        if key in metrics:
            lines.append(f"{label}: {metrics[key]:.1f}")

    panel_h = (len(lines) + 1) * line_h
    px_start = w - panel_w - 10
    py_start = 10

    panel_ov = img.copy()
    cv2.rectangle(panel_ov, (px_start, py_start), (px_start + panel_w, py_start + panel_h), (40, 40, 40), -1)
    img = cv2.addWeighted(panel_ov, 0.7, img, 0.3, 0)

    for i, line in enumerate(lines):
        y_pos = py_start + (i + 1) * line_h
        if line == "---":
            cv2.line(img, (px_start + 5, y_pos - 5), (px_start + panel_w - 5, y_pos - 5), (100, 100, 100), 1)
            continue
        color = (255, 255, 255)
        if "PHASE" in line:
            color = (100, 255, 100)
        elif "Hip" in line:
            color = bgr(COLORS_RGB["hip"])
        elif "Shoulder" in line:
            color = bgr(COLORS_RGB["shoulder"])
        elif "Spine" in line:
            color = bgr(COLORS_RGB["spine"])
        cv2.putText(img, line, (px_start + 8, y_pos), cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.85, color, 1, cv2.LINE_AA)

    return img
