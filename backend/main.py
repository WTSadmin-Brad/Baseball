"""
Baseball Swing Analysis — FastAPI Backend
"""

import json
import shutil
import uuid
from pathlib import Path

import cv2
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .models import LandmarkUpdate, SessionData, FrameData, Landmark, VideoInfo
from .pose_engine import (
    detect_landmarks,
    compute_metrics,
    render_annotated_frame,
    SWING_PHASES,
    SKELETON_CONNECTIONS,
    COLORS_RGB,
    LANDMARK_NAMES,
    SWING_LANDMARKS,
)
from .video_extract import (
    extract_all_frames,
    get_video_info,
    extract_frame_at_index,
    save_frame,
    generate_thumbnail,
)

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="Swing Analysis", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
SESSIONS_DIR = BASE_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def session_dir(session_id: str) -> Path:
    d = SESSIONS_DIR / session_id
    if not d.exists():
        raise HTTPException(404, f"Session {session_id} not found")
    return d


def load_session_state(session_id: str) -> dict:
    state_path = session_dir(session_id) / "state.json"
    if not state_path.exists():
        raise HTTPException(404, "Session state not found")
    return json.loads(state_path.read_text())


def save_session_state(session_id: str, state: dict):
    state_path = SESSIONS_DIR / session_id / "state.json"
    state_path.write_text(json.dumps(state, indent=2))


# ── API Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/upload/images")
async def upload_images(files: list[UploadFile] = File(...)):
    """Upload image files to create a new session."""
    session_id = str(uuid.uuid4())[:8]
    sdir = SESSIONS_DIR / session_id
    sdir.mkdir(parents=True)
    (sdir / "frames").mkdir()
    (sdir / "thumbnails").mkdir()
    (sdir / "annotated").mkdir()

    frame_list = []
    for i, f in enumerate(sorted(files, key=lambda x: x.filename)):
        ext = Path(f.filename).suffix or ".jpg"
        frame_path = sdir / "frames" / f"{i:02d}{ext}"
        with open(frame_path, "wb") as out:
            content = await f.read()
            out.write(content)

        # Generate thumbnail
        img = cv2.imread(str(frame_path))
        if img is not None:
            thumb = generate_thumbnail(img)
            save_frame(thumb, str(sdir / "thumbnails" / f"{i:02d}.jpg"))

        phase = SWING_PHASES[i] if i < len(SWING_PHASES) else f"Frame {i+1}"
        frame_list.append({
            "frame_id": i,
            "filename": f.filename,
            "phase": phase,
            "landmarks": None,
            "metrics": None,
            "image_width": img.shape[1] if img is not None else 0,
            "image_height": img.shape[0] if img is not None else 0,
        })

    state = {"session_id": session_id, "frames": frame_list, "annotations": {}}
    save_session_state(session_id, state)

    return {"session_id": session_id, "frame_count": len(frame_list)}


@app.post("/api/upload/video")
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file, extract frames for selection."""
    session_id = str(uuid.uuid4())[:8]
    sdir = SESSIONS_DIR / session_id
    sdir.mkdir(parents=True)
    (sdir / "video_frames").mkdir()
    (sdir / "thumbnails").mkdir()
    (sdir / "frames").mkdir()
    (sdir / "annotated").mkdir()

    # Save video
    video_path = sdir / f"video{Path(file.filename).suffix}"
    with open(video_path, "wb") as out:
        content = await file.read()
        out.write(content)

    # Get info
    info = get_video_info(str(video_path))

    # Extract frames at ~10fps for browsing
    all_frames = extract_all_frames(str(video_path), target_fps=10.0)
    for i, frame in enumerate(all_frames):
        save_frame(frame, str(sdir / "video_frames" / f"{i:04d}.jpg"))
        thumb = generate_thumbnail(frame)
        save_frame(thumb, str(sdir / "thumbnails" / f"v_{i:04d}.jpg"))

    state = {
        "session_id": session_id,
        "video_path": str(video_path),
        "video_info": info,
        "video_frame_count": len(all_frames),
        "selected_frames": [],
        "frames": [],
        "annotations": {},
    }
    save_session_state(session_id, state)

    return {
        "session_id": session_id,
        "video_info": info,
        "extracted_frame_count": len(all_frames),
    }


@app.post("/api/video/{session_id}/select-frames")
async def select_video_frames(session_id: str, frame_indices: list[int]):
    """Select specific extracted video frames to use for analysis."""
    state = load_session_state(session_id)
    sdir = session_dir(session_id)

    frame_list = []
    for i, vidx in enumerate(sorted(frame_indices)):
        src = sdir / "video_frames" / f"{vidx:04d}.jpg"
        if not src.exists():
            raise HTTPException(400, f"Video frame {vidx} not found")
        dst = sdir / "frames" / f"{i:02d}.jpg"
        shutil.copy2(src, dst)

        img = cv2.imread(str(dst))
        phase = SWING_PHASES[i] if i < len(SWING_PHASES) else f"Frame {i+1}"
        frame_list.append({
            "frame_id": i,
            "filename": f"frame_{vidx:04d}.jpg",
            "phase": phase,
            "landmarks": None,
            "metrics": None,
            "image_width": img.shape[1] if img is not None else 0,
            "image_height": img.shape[0] if img is not None else 0,
        })

    state["selected_frames"] = frame_indices
    state["frames"] = frame_list
    save_session_state(session_id, state)
    return {"frame_count": len(frame_list)}


@app.post("/api/detect/{session_id}")
async def run_detection(session_id: str):
    """Run pose detection on all frames in a session."""
    state = load_session_state(session_id)
    sdir = session_dir(session_id)

    for frame in state["frames"]:
        fid = frame["frame_id"]
        img_path = sdir / "frames" / f"{fid:02d}.jpg"
        if not img_path.exists():
            # Try other extensions
            for ext in [".jpeg", ".png"]:
                alt = sdir / "frames" / f"{fid:02d}{ext}"
                if alt.exists():
                    img_path = alt
                    break

        landmarks = detect_landmarks(str(img_path))
        if landmarks:
            frame["landmarks"] = landmarks
            metrics = compute_metrics(landmarks, frame["image_width"], frame["image_height"])
            frame["metrics"] = metrics

            # Render annotated frame
            annotated = render_annotated_frame(
                str(img_path), landmarks, metrics, frame["phase"]
            )
            cv2.imwrite(
                str(sdir / "annotated" / f"{fid:02d}.jpg"),
                annotated,
                [cv2.IMWRITE_JPEG_QUALITY, 95],
            )

    save_session_state(session_id, state)
    return {"status": "done", "frames_detected": sum(1 for f in state["frames"] if f["landmarks"])}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get full session data including landmarks and metrics."""
    state = load_session_state(session_id)
    return state


@app.get("/api/frame/{session_id}/{frame_id}/image")
async def get_frame_image(session_id: str, frame_id: int):
    """Get the original frame image."""
    sdir = session_dir(session_id)
    for ext in [".jpg", ".jpeg", ".png"]:
        p = sdir / "frames" / f"{frame_id:02d}{ext}"
        if p.exists():
            return FileResponse(p, media_type="image/jpeg")
    raise HTTPException(404, "Frame not found")


@app.get("/api/frame/{session_id}/{frame_id}/annotated")
async def get_annotated_frame(session_id: str, frame_id: int):
    """Get the annotated frame image."""
    sdir = session_dir(session_id)
    p = sdir / "annotated" / f"{frame_id:02d}.jpg"
    if not p.exists():
        raise HTTPException(404, "Annotated frame not found")
    return FileResponse(p, media_type="image/jpeg")


@app.get("/api/frame/{session_id}/{frame_id}/thumbnail")
async def get_thumbnail(session_id: str, frame_id: int):
    """Get a frame thumbnail."""
    sdir = session_dir(session_id)
    p = sdir / "thumbnails" / f"{frame_id:02d}.jpg"
    if not p.exists():
        raise HTTPException(404, "Thumbnail not found")
    return FileResponse(p, media_type="image/jpeg")


@app.get("/api/video-frame/{session_id}/{frame_index}/thumbnail")
async def get_video_frame_thumbnail(session_id: str, frame_index: int):
    """Get a video frame thumbnail for the frame selector."""
    sdir = session_dir(session_id)
    p = sdir / "thumbnails" / f"v_{frame_index:04d}.jpg"
    if not p.exists():
        raise HTTPException(404, "Video frame thumbnail not found")
    return FileResponse(p, media_type="image/jpeg")


@app.put("/api/landmarks/{session_id}/{frame_id}")
async def update_landmarks(session_id: str, frame_id: int, update: LandmarkUpdate):
    """Update landmarks for a specific frame (manual adjustment)."""
    state = load_session_state(session_id)
    sdir = session_dir(session_id)

    frame = None
    for f in state["frames"]:
        if f["frame_id"] == frame_id:
            frame = f
            break
    if not frame:
        raise HTTPException(404, f"Frame {frame_id} not found")

    # Update landmarks
    new_landmarks = [lm.model_dump() for lm in update.landmarks]
    frame["landmarks"] = new_landmarks

    # Recompute metrics
    metrics = compute_metrics(new_landmarks, frame["image_width"], frame["image_height"])
    frame["metrics"] = metrics

    # Re-render annotated frame
    img_path = sdir / "frames" / f"{frame_id:02d}.jpg"
    if not img_path.exists():
        for ext in [".jpeg", ".png"]:
            alt = sdir / "frames" / f"{frame_id:02d}{ext}"
            if alt.exists():
                img_path = alt
                break

    annotated = render_annotated_frame(str(img_path), new_landmarks, metrics, frame["phase"])
    cv2.imwrite(str(sdir / "annotated" / f"{frame_id:02d}.jpg"), annotated, [cv2.IMWRITE_JPEG_QUALITY, 95])

    save_session_state(session_id, state)
    return {"metrics": metrics}


@app.put("/api/annotations/{session_id}/{frame_id}")
async def save_annotations(session_id: str, frame_id: int, annotations: list[dict]):
    """Save drawing annotations for a frame."""
    state = load_session_state(session_id)
    if "annotations" not in state:
        state["annotations"] = {}
    state["annotations"][str(frame_id)] = annotations
    save_session_state(session_id, state)
    return {"status": "saved"}


@app.get("/api/config")
async def get_config():
    """Get rendering configuration (colors, connections, landmark names)."""
    return {
        "colors": COLORS_RGB,
        "connections": [
            {"from": a, "to": b, "group": g} for a, b, g in SKELETON_CONNECTIONS
        ],
        "landmark_names": LANDMARK_NAMES,
        "swing_landmarks": SWING_LANDMARKS,
        "swing_phases": SWING_PHASES,
    }


# ── Serve built frontend (production) ───────────────────────────────────────
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="frontend-assets")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        """Serve frontend SPA — all non-API routes fall through to index.html."""
        file_path = FRONTEND_DIST / path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
