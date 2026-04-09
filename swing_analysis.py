"""
Baseball Swing Pose Analysis System
====================================
Detects body pose landmarks using MediaPipe and overlays swing-mechanics
markers, skeletal lines, key angles, and rotation metrics on each frame.

Swing phases based on 9U Hitting Guide, Assessment Form, and Hitting Checklist.
"""

import cv2
import math
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
import os
import json
from pathlib import Path

# ── MediaPipe model path ─────────────────────────────────────────────────────
MODEL_PATH = "/home/user/Baseball/pose_landmarker_heavy.task"

# ── Swing phase labels mapped to frame order ─────────────────────────────────
SWING_PHASES = [
    "1 - Stance / Setup",
    "2 - Early Load",
    "3 - Load / Stride",
    "4 - Launch Position",
    "5 - Swing Initiation",
    "6 - Connection / Approach",
    "7 - Contact / Extension",
    "8 - Follow-Through / Finish",
]

# ── Color palette (BGR for OpenCV) ───────────────────────────────────────────
COLORS = {
    "hip_line":        (0, 100, 255),    # Orange – hip rotation
    "shoulder_line":   (255, 200, 0),    # Cyan – shoulder rotation
    "spine":           (255, 255, 255),  # White – posture
    "front_arm":       (0, 255, 100),    # Green – front arm
    "back_arm":        (100, 255, 0),    # Green variant – back arm
    "front_leg":       (0, 230, 255),    # Yellow – front leg
    "back_leg":        (0, 200, 230),    # Yellow variant – back leg
    "head":            (255, 255, 255),  # White – head/eyes
    "plumb":           (200, 200, 200),  # Gray – vertical plumb line
    "angle_arc":       (180, 180, 255),  # Light red – angle arcs
    "separation_arc":  (0, 255, 255),    # Yellow – hip-shoulder separation
    "bat_line":        (0, 180, 255),    # Orange – bat approximation
    "marker":          (0, 0, 255),      # Red – joint markers
    "text_bg":         (40, 40, 40),     # Dark bg for text
    "text":            (255, 255, 255),  # White text
}

# Marker radius scales with image size
MARKER_RADIUS_RATIO = 0.008
LINE_THICKNESS_RATIO = 0.004
THIN_LINE_RATIO = 0.002


# ── Utility functions ────────────────────────────────────────────────────────

def angle_between_points(a, b, c):
    """Angle at point b formed by points a-b-c, in degrees."""
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    return math.degrees(math.acos(np.clip(cos_angle, -1.0, 1.0)))


def line_angle_from_horizontal(p1, p2):
    """Angle of line p1->p2 relative to horizontal, in degrees.
    Positive = p2 is above p1 (in image coords, y goes down, so we invert)."""
    dx = p2[0] - p1[0]
    dy = -(p2[1] - p1[1])  # Invert y because image y-axis is flipped
    return math.degrees(math.atan2(dy, dx))


def midpoint(p1, p2):
    return ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)


def draw_arc(img, center, radius, start_angle, end_angle, color, thickness=2):
    """Draw an arc on the image."""
    axes = (radius, radius)
    # OpenCV ellipse uses clockwise angles from 3 o'clock
    cv2.ellipse(img, center, axes, 0, -end_angle, -start_angle, color, thickness)


def draw_angle_label(img, center, angle_val, label, color, font_scale, offset=(0, -15)):
    """Draw an angle value with a label near a point, clamped to image bounds."""
    h_img, w_img = img.shape[:2]
    text = f"{label}: {angle_val:.0f}"
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)
    # Calculate position and clamp to image bounds
    px = max(4, min(center[0] + offset[0], w_img - tw - 6))
    py = max(th + 6, min(center[1] + offset[1], h_img - 6))
    cv2.rectangle(img, (px - 2, py - th - 3), (px + tw + 4, py + 3), COLORS["text_bg"], -1)
    cv2.putText(img, text, (px, py), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 1, cv2.LINE_AA)


def get_landmark_px(landmarks, idx, w, h):
    """Get pixel coordinates for a landmark. Returns (x, y) or None if low visibility."""
    lm = landmarks[idx]
    if lm.visibility is not None and lm.visibility < 0.15:
        return None
    return (int(lm.x * w), int(lm.y * h))


def draw_line_safe(img, p1, p2, color, thickness):
    """Draw a line only if both points exist."""
    if p1 is not None and p2 is not None:
        cv2.line(img, p1, p2, color, thickness, cv2.LINE_AA)
        return True
    return False


def draw_marker(img, pt, color, radius, filled=True):
    """Draw a circular marker at a point."""
    if pt is not None:
        cv2.circle(img, pt, radius, color, -1 if filled else 2, cv2.LINE_AA)
        # White border
        cv2.circle(img, pt, radius, (255, 255, 255), 1, cv2.LINE_AA)


# ── Main annotation function ────────────────────────────────────────────────

def annotate_frame(image_path, phase_label, output_path):
    """
    Run pose detection on a single frame and draw all swing-analysis overlays.
    Returns a dict of computed metrics.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"  ERROR: Could not read {image_path}")
        return None

    h, w = img.shape[:2]
    marker_r = max(4, int(w * MARKER_RADIUS_RATIO))
    line_thick = max(2, int(w * LINE_THICKNESS_RATIO))
    thin_thick = max(1, int(w * THIN_LINE_RATIO))
    font_scale = max(0.35, w / 1800)
    arc_radius = max(20, int(w * 0.04))

    # Run MediaPipe Pose (Tasks API)
    options = vision.PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
    )
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                            data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        results = landmarker.detect(mp_image)

    if not results.pose_landmarks or len(results.pose_landmarks) == 0:
        print(f"  WARNING: No pose detected in {image_path}")
        cv2.putText(img, phase_label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX,
                     font_scale * 1.5, COLORS["text"], 2, cv2.LINE_AA)
        cv2.imwrite(str(output_path), img)
        return None

    lm = results.pose_landmarks[0]  # First (only) person

    # ── Extract key landmarks ────────────────────────────────────────────
    pts = {}
    landmark_map = {
        "nose": 0, "left_ear": 7, "right_ear": 8,
        "left_shoulder": 11, "right_shoulder": 12,
        "left_elbow": 13, "right_elbow": 14,
        "left_wrist": 15, "right_wrist": 16,
        "left_hip": 23, "right_hip": 24,
        "left_knee": 25, "right_knee": 26,
        "left_ankle": 27, "right_ankle": 28,
        "left_pinky": 17, "right_pinky": 18,
        "left_index": 19, "right_index": 20,
        "left_heel": 29, "right_heel": 30,
        "left_foot_index": 31, "right_foot_index": 32,
    }

    for name, idx in landmark_map.items():
        pts[name] = get_landmark_px(lm, idx, w, h)

    # Derived points
    if pts["left_shoulder"] and pts["right_shoulder"]:
        pts["mid_shoulder"] = midpoint(pts["left_shoulder"], pts["right_shoulder"])
    else:
        pts["mid_shoulder"] = None

    if pts["left_hip"] and pts["right_hip"]:
        pts["mid_hip"] = midpoint(pts["left_hip"], pts["right_hip"])
    else:
        pts["mid_hip"] = None

    # Create overlay for semi-transparent drawing
    overlay = img.copy()

    # ── 1. SKELETAL LINES ────────────────────────────────────────────────

    # Shoulder line (cyan) — shows shoulder rotation/tilt
    draw_line_safe(overlay, pts["left_shoulder"], pts["right_shoulder"],
                   COLORS["shoulder_line"], line_thick)

    # Hip line (orange) — shows hip rotation/tilt
    draw_line_safe(overlay, pts["left_hip"], pts["right_hip"],
                   COLORS["hip_line"], line_thick)

    # Spine (white) — posture
    draw_line_safe(overlay, pts["mid_shoulder"], pts["mid_hip"],
                   COLORS["spine"], line_thick)

    # Front arm (left side in these images = front for RH batter)
    draw_line_safe(overlay, pts["left_shoulder"], pts["left_elbow"],
                   COLORS["front_arm"], line_thick)
    draw_line_safe(overlay, pts["left_elbow"], pts["left_wrist"],
                   COLORS["front_arm"], line_thick)

    # Back arm
    draw_line_safe(overlay, pts["right_shoulder"], pts["right_elbow"],
                   COLORS["back_arm"], line_thick)
    draw_line_safe(overlay, pts["right_elbow"], pts["right_wrist"],
                   COLORS["back_arm"], line_thick)

    # Front leg
    draw_line_safe(overlay, pts["left_hip"], pts["left_knee"],
                   COLORS["front_leg"], line_thick)
    draw_line_safe(overlay, pts["left_knee"], pts["left_ankle"],
                   COLORS["front_leg"], line_thick)

    # Back leg
    draw_line_safe(overlay, pts["right_hip"], pts["right_knee"],
                   COLORS["back_leg"], line_thick)
    draw_line_safe(overlay, pts["right_knee"], pts["right_ankle"],
                   COLORS["back_leg"], line_thick)

    # Head — nose to mid-ears approximation
    draw_line_safe(overlay, pts["nose"], pts["mid_shoulder"],
                   COLORS["head"], thin_thick)

    # Wrist-to-wrist line (approximates hand/bat connection)
    draw_line_safe(overlay, pts["left_wrist"], pts["right_wrist"],
                   COLORS["bat_line"], thin_thick)

    # Wrist to index finger lines (bat direction approximation)
    draw_line_safe(overlay, pts["left_wrist"], pts["left_index"],
                   COLORS["bat_line"], thin_thick)
    draw_line_safe(overlay, pts["right_wrist"], pts["right_index"],
                   COLORS["bat_line"], thin_thick)

    # ── 2. VERTICAL PLUMB LINE (balance reference) ───────────────────────
    if pts["nose"]:
        plumb_top = (pts["nose"][0], 0)
        plumb_bot = (pts["nose"][0], h)
        cv2.line(overlay, plumb_top, plumb_bot, COLORS["plumb"], thin_thick, cv2.LINE_AA)

    # ── 3. ROTATION REFERENCE LINES ──────────────────────────────────────
    # Extend hip and shoulder lines to show rotation direction
    extend_len = int(w * 0.06)

    if pts["left_hip"] and pts["right_hip"]:
        dx = pts["right_hip"][0] - pts["left_hip"][0]
        dy = pts["right_hip"][1] - pts["left_hip"][1]
        length = math.sqrt(dx*dx + dy*dy) + 1e-8
        ux, uy = dx/length, dy/length
        # Extend both ends with dashed appearance
        ext_l = (int(pts["left_hip"][0] - ux * extend_len),
                 int(pts["left_hip"][1] - uy * extend_len))
        ext_r = (int(pts["right_hip"][0] + ux * extend_len),
                 int(pts["right_hip"][1] + uy * extend_len))
        cv2.line(overlay, ext_l, pts["left_hip"], COLORS["hip_line"], thin_thick, cv2.LINE_AA)
        cv2.line(overlay, pts["right_hip"], ext_r, COLORS["hip_line"], thin_thick, cv2.LINE_AA)

    if pts["left_shoulder"] and pts["right_shoulder"]:
        dx = pts["right_shoulder"][0] - pts["left_shoulder"][0]
        dy = pts["right_shoulder"][1] - pts["left_shoulder"][1]
        length = math.sqrt(dx*dx + dy*dy) + 1e-8
        ux, uy = dx/length, dy/length
        ext_l = (int(pts["left_shoulder"][0] - ux * extend_len),
                 int(pts["left_shoulder"][1] - uy * extend_len))
        ext_r = (int(pts["right_shoulder"][0] + ux * extend_len),
                 int(pts["right_shoulder"][1] + uy * extend_len))
        cv2.line(overlay, ext_l, pts["left_shoulder"], COLORS["shoulder_line"], thin_thick, cv2.LINE_AA)
        cv2.line(overlay, pts["right_shoulder"], ext_r, COLORS["shoulder_line"], thin_thick, cv2.LINE_AA)

    # Blend overlay
    alpha = 0.85
    img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    # ── 4. JOINT MARKERS ─────────────────────────────────────────────────
    # Different colors for different body regions
    joint_colors = {
        "nose": COLORS["head"],
        "left_ear": COLORS["head"], "right_ear": COLORS["head"],
        "left_shoulder": COLORS["shoulder_line"], "right_shoulder": COLORS["shoulder_line"],
        "left_elbow": COLORS["front_arm"], "right_elbow": COLORS["back_arm"],
        "left_wrist": COLORS["front_arm"], "right_wrist": COLORS["back_arm"],
        "left_hip": COLORS["hip_line"], "right_hip": COLORS["hip_line"],
        "left_knee": COLORS["front_leg"], "right_knee": COLORS["back_leg"],
        "left_ankle": COLORS["front_leg"], "right_ankle": COLORS["back_leg"],
    }

    for name, color in joint_colors.items():
        draw_marker(img, pts[name], color, marker_r)

    # Mid-points get slightly smaller markers
    draw_marker(img, pts["mid_shoulder"], COLORS["spine"], marker_r - 1)
    draw_marker(img, pts["mid_hip"], COLORS["spine"], marker_r - 1)

    # ── 5. COMPUTE AND DISPLAY KEY ANGLES ────────────────────────────────
    metrics = {"phase": phase_label}

    # Back elbow angle (connection/slot)
    if pts["right_shoulder"] and pts["right_elbow"] and pts["right_wrist"]:
        angle = angle_between_points(pts["right_shoulder"], pts["right_elbow"], pts["right_wrist"])
        metrics["back_elbow_angle"] = angle
        draw_arc(img, pts["right_elbow"], arc_radius, 0, int(angle),
                 COLORS["angle_arc"], thin_thick + 1)
        draw_angle_label(img, pts["right_elbow"], angle, "Back Elbow",
                        COLORS["back_arm"], font_scale, offset=(10, -10))

    # Front elbow angle
    if pts["left_shoulder"] and pts["left_elbow"] and pts["left_wrist"]:
        angle = angle_between_points(pts["left_shoulder"], pts["left_elbow"], pts["left_wrist"])
        metrics["front_elbow_angle"] = angle
        draw_angle_label(img, pts["left_elbow"], angle, "Front Elbow",
                        COLORS["front_arm"], font_scale, offset=(-150, -10))

    # Front knee angle (firmness of front side)
    if pts["left_hip"] and pts["left_knee"] and pts["left_ankle"]:
        angle = angle_between_points(pts["left_hip"], pts["left_knee"], pts["left_ankle"])
        metrics["front_knee_angle"] = angle
        draw_arc(img, pts["left_knee"], arc_radius, 0, int(angle),
                 COLORS["angle_arc"], thin_thick + 1)
        draw_angle_label(img, pts["left_knee"], angle, "Front Knee",
                        COLORS["front_leg"], font_scale, offset=(-150, 20))

    # Back knee angle (drive)
    if pts["right_hip"] and pts["right_knee"] and pts["right_ankle"]:
        angle = angle_between_points(pts["right_hip"], pts["right_knee"], pts["right_ankle"])
        metrics["back_knee_angle"] = angle
        draw_angle_label(img, pts["right_knee"], angle, "Back Knee",
                        COLORS["back_leg"], font_scale, offset=(10, 20))

    # Spine angle (tilt from vertical)
    if pts["mid_shoulder"] and pts["mid_hip"]:
        # Angle of spine from vertical
        dx = pts["mid_shoulder"][0] - pts["mid_hip"][0]
        dy = pts["mid_shoulder"][1] - pts["mid_hip"][1]
        spine_angle = math.degrees(math.atan2(abs(dx), abs(dy)))
        metrics["spine_tilt"] = spine_angle
        # Draw small label near spine midpoint
        spine_mid = midpoint(pts["mid_shoulder"], pts["mid_hip"])
        draw_angle_label(img, spine_mid, spine_angle, "Spine Tilt",
                        COLORS["spine"], font_scale, offset=(15, 0))

    # ── 6. HIP AND SHOULDER ROTATION + SEPARATION ────────────────────────
    hip_angle = None
    shoulder_angle = None

    if pts["left_hip"] and pts["right_hip"]:
        hip_angle = line_angle_from_horizontal(pts["left_hip"], pts["right_hip"])
        metrics["hip_line_angle"] = hip_angle

    if pts["left_shoulder"] and pts["right_shoulder"]:
        shoulder_angle = line_angle_from_horizontal(pts["left_shoulder"], pts["right_shoulder"])
        metrics["shoulder_line_angle"] = shoulder_angle

    if hip_angle is not None and shoulder_angle is not None:
        # Normalize angular difference to [-180, 180] range
        raw_diff = shoulder_angle - hip_angle
        separation = abs((raw_diff + 180) % 360 - 180)
        metrics["hip_shoulder_separation"] = separation

    # ── 7. METRICS PANEL ─────────────────────────────────────────────────
    # Draw a semi-transparent panel at top-right with key metrics
    panel_w = int(w * 0.48)
    panel_h_per_line = max(16, int(font_scale * 30))
    panel_lines = []
    panel_lines.append(f"PHASE: {phase_label}")
    panel_lines.append("---")

    if "hip_line_angle" in metrics:
        panel_lines.append(f"Hip Line Angle: {metrics['hip_line_angle']:.1f} deg")
    if "shoulder_line_angle" in metrics:
        panel_lines.append(f"Shoulder Line Angle: {metrics['shoulder_line_angle']:.1f} deg")
    if "hip_shoulder_separation" in metrics:
        panel_lines.append(f"Hip-Shoulder Separation: {metrics['hip_shoulder_separation']:.1f} deg")
    panel_lines.append("---")

    if "back_elbow_angle" in metrics:
        panel_lines.append(f"Back Elbow: {metrics['back_elbow_angle']:.0f} deg")
    if "front_elbow_angle" in metrics:
        panel_lines.append(f"Front Elbow: {metrics['front_elbow_angle']:.0f} deg")
    if "front_knee_angle" in metrics:
        panel_lines.append(f"Front Knee: {metrics['front_knee_angle']:.0f} deg")
    if "back_knee_angle" in metrics:
        panel_lines.append(f"Back Knee: {metrics['back_knee_angle']:.0f} deg")
    if "spine_tilt" in metrics:
        panel_lines.append(f"Spine Tilt: {metrics['spine_tilt']:.1f} deg")

    panel_h = (len(panel_lines) + 1) * panel_h_per_line
    panel_x = w - panel_w - 10
    panel_y = 10

    # Semi-transparent background
    panel_overlay = img.copy()
    cv2.rectangle(panel_overlay, (panel_x, panel_y),
                  (panel_x + panel_w, panel_y + panel_h),
                  COLORS["text_bg"], -1)
    img = cv2.addWeighted(panel_overlay, 0.7, img, 0.3, 0)

    # Draw text
    for i, line in enumerate(panel_lines):
        y_pos = panel_y + (i + 1) * panel_h_per_line
        if line == "---":
            cv2.line(img, (panel_x + 5, y_pos - 5),
                     (panel_x + panel_w - 5, y_pos - 5),
                     (100, 100, 100), 1)
            continue

        color = COLORS["text"]
        if "Hip Line" in line or "Hip-Shoulder" in line:
            color = COLORS["hip_line"]
        elif "Shoulder Line" in line:
            color = COLORS["shoulder_line"]
        elif "Spine" in line:
            color = COLORS["spine"]
        elif "PHASE" in line:
            color = (100, 255, 100)  # Green for phase

        cv2.putText(img, line, (panel_x + 8, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.85,
                    color, 1, cv2.LINE_AA)

    # ── 8. LEGEND (bottom-left) ──────────────────────────────────────────
    legend_items = [
        ("Shoulders", COLORS["shoulder_line"]),
        ("Hips", COLORS["hip_line"]),
        ("Spine/Posture", COLORS["spine"]),
        ("Front Arm", COLORS["front_arm"]),
        ("Back Arm", COLORS["back_arm"]),
        ("Front Leg", COLORS["front_leg"]),
        ("Back Leg", COLORS["back_leg"]),
        ("Balance Plumb", COLORS["plumb"]),
    ]
    legend_y = h - len(legend_items) * panel_h_per_line - 10
    legend_x = 10

    # Background
    leg_overlay = img.copy()
    cv2.rectangle(leg_overlay, (legend_x, legend_y - 5),
                  (legend_x + int(w * 0.22), h - 5),
                  COLORS["text_bg"], -1)
    img = cv2.addWeighted(leg_overlay, 0.7, img, 0.3, 0)

    for i, (label, color) in enumerate(legend_items):
        y_pos = legend_y + (i + 1) * panel_h_per_line
        cv2.circle(img, (legend_x + 10, y_pos - 5), marker_r, color, -1)
        cv2.putText(img, label, (legend_x + 25, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale * 0.7,
                    color, 1, cv2.LINE_AA)

    # Save
    cv2.imwrite(str(output_path), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"  Saved: {output_path}")
    return metrics


# ── Composite grid builder ───────────────────────────────────────────────────

def build_composite_grid(annotated_paths, output_path, cols=4):
    """Build a composite image showing all frames in a grid."""
    images = [cv2.imread(str(p)) for p in annotated_paths]
    images = [img for img in images if img is not None]
    if not images:
        return

    # Resize all to same dimensions
    target_h = min(img.shape[0] for img in images)
    target_w = min(img.shape[1] for img in images)
    images = [cv2.resize(img, (target_w, target_h)) for img in images]

    rows_needed = math.ceil(len(images) / cols)
    # Pad with black if needed
    while len(images) < rows_needed * cols:
        images.append(np.zeros_like(images[0]))

    grid_rows = []
    for r in range(rows_needed):
        row_imgs = images[r * cols : (r + 1) * cols]
        grid_rows.append(np.hstack(row_imgs))

    grid = np.vstack(grid_rows)

    # Add title bar
    title_h = 60
    title_bar = np.zeros((title_h, grid.shape[1], 3), dtype=np.uint8)
    title_bar[:] = (40, 40, 40)
    cv2.putText(title_bar, "Swing Sequence Analysis - Pose Markers & Rotation Metrics",
                (20, 42), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
    grid = np.vstack([title_bar, grid])

    cv2.imwrite(str(output_path), grid, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"\nComposite grid saved: {output_path}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    base_dir = Path("/home/user/Baseball")
    output_dir = base_dir / "annotated"
    output_dir.mkdir(exist_ok=True)

    # Frame images in order
    frame_files = sorted(base_dir.glob("IMG_*.jpeg"))
    print(f"Found {len(frame_files)} frames: {[f.name for f in frame_files]}")

    if len(frame_files) != 8:
        print(f"WARNING: Expected 8 frames, found {len(frame_files)}")

    all_metrics = []
    annotated_paths = []

    for i, frame_path in enumerate(frame_files):
        phase = SWING_PHASES[i] if i < len(SWING_PHASES) else f"Frame {i+1}"
        print(f"\nProcessing {frame_path.name} — {phase}")
        out_path = output_dir / f"frame_{i+1:02d}_{frame_path.stem}.jpg"
        metrics = annotate_frame(frame_path, phase, out_path)
        if metrics:
            all_metrics.append(metrics)
        annotated_paths.append(out_path)

    # Build composite grid
    build_composite_grid(annotated_paths, output_dir / "composite_grid.jpg")

    # Save metrics JSON
    metrics_path = output_dir / "swing_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\nMetrics saved: {metrics_path}")

    # Print summary table
    print("\n" + "=" * 80)
    print("SWING METRICS SUMMARY")
    print("=" * 80)
    print(f"{'Phase':<32} {'Hip Rot':>8} {'Shld Rot':>9} {'Sep':>6} {'Spine':>7} {'Back Elb':>9} {'Frt Knee':>9}")
    print("-" * 80)
    for m in all_metrics:
        print(f"{m.get('phase', '?'):<32} "
              f"{m.get('hip_line_angle', 0):>7.1f}° "
              f"{m.get('shoulder_line_angle', 0):>8.1f}° "
              f"{m.get('hip_shoulder_separation', 0):>5.1f}° "
              f"{m.get('spine_tilt', 0):>6.1f}° "
              f"{m.get('back_elbow_angle', 0):>8.0f}° "
              f"{m.get('front_knee_angle', 0):>8.0f}°")
    print("=" * 80)


if __name__ == "__main__":
    main()
