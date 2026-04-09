# Swing Analysis App

Youth baseball swing analysis tool with automatic pose detection, interactive marker editing, and swing metrics tracking.

## Architecture

**Backend** — FastAPI (Python) at `backend/`
- `main.py` — REST API: image/video upload, pose detection, landmark editing, session management, serves built frontend
- `pose_engine.py` — MediaPipe Pose (heavy model) landmark detection, angle/rotation metric computation, annotated frame rendering
- `video_extract.py` — OpenCV video frame extraction + thumbnails
- `models.py` — Pydantic schemas

**Frontend** — React + Vite at `frontend/`
- `FrameViewer.jsx` — Main viewer with three modes: Annotated (server-rendered overlays), Markers (Canvas with draggable landmarks), Original
- `FrameCarousel.jsx` — Thumbnail strip navigation across swing phases
- `MetricsPanel.jsx` — Color-coded angle readouts per frame
- `MetricsChart.jsx` — Recharts line chart of metrics across all phases
- `UploadPanel.jsx` — Drag-and-drop for images or video
- `VideoFrameSelector.jsx` — Pick key frames from uploaded video
- `useSession.js` — Hook managing all API calls and session state

**Original CLI** — `swing_analysis.py` (kept as reference, standalone script that processes 8 JPEGs)

## How to Run

```bash
# One-time setup
pip install -r requirements.txt
cd frontend && npm install && npx vite build && cd ..
# Download pose model (30MB) if missing:
python3 -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task', 'pose_landmarker_heavy.task')"

# Production (single server)
uvicorn backend.main:app --port 8000

# Dev (hot reload)
# Terminal 1: uvicorn backend.main:app --reload --port 8000
# Terminal 2: cd frontend && npm run dev   (localhost:5173, proxies /api to :8000)
```

## Key Technical Decisions

- **MediaPipe Pose (heavy model)** over lighter models — accuracy matters more than speed for static image analysis
- **FastAPI** — async, built-in OpenAPI docs, clean file upload handling, Python ecosystem matches pose engine
- **React + Vite** over vanilla JS — feature set warrants components (Canvas interactions, state for marker positions, charts, undo/redo)
- **Recharts** for metrics visualization
- **File-based sessions** under `sessions/` — no database needed for local single-user tool
- **Normalized landmark coordinates** [0,1] stored in session state — pixel conversion happens at render time

## Swing Phase Framework

8-frame sequence mapped to swing phases. See @.claude/rules/swing-mechanics.md for detailed mechanics.

| Frame | Phase | Key Checkpoints |
|-------|-------|----------------|
| 1 | Stance / Setup | Athletic position, grip, balance, bat angle |
| 2 | Early Load | Rhythm, weight shift back, hands working back |
| 3 | Load / Stride | Coil into back hip, small step forward |
| 4 | Launch Position | Front foot landed, hands back, balanced, ready |
| 5 | Swing Initiation | Hips fire first (lower half leads), core engagement |
| 6 | Connection / Approach | Bat path inside the ball, back elbow slots, staying connected |
| 7 | Contact / Extension | Palm up/palm down, extension through ball, contact point |
| 8 | Follow-Through / Finish | Balanced finish, chin on back shoulder |

## Tracked Metrics

- **Hip-Shoulder Separation** — difference between hip and shoulder rotation angles (measures sequencing / "tornado effect")
- **Hip/Shoulder Line Angles** — rotation from horizontal
- **Back/Front Elbow Angles** — connection, slot, lead arm extension
- **Front/Back Knee Angles** — front side firmness, back leg drive
- **Spine Tilt** — posture maintenance through swing

## Color Palette (consistent across backend rendering and frontend Canvas)

- Cyan `#00c8ff` — Shoulders
- Orange `#ff6400` — Hips
- White `#ffffff` — Spine/posture
- Green `#64ff00` / `#00ff64` — Front/back arms
- Yellow `#ffe600` / `#e6c800` — Front/back legs

## Current Status

**Completed (Phases 1-4):**
- CLI pose analysis script with annotated output
- FastAPI backend with full REST API
- React frontend: upload, frame viewer, marker editing, metrics panel, charts, video upload + frame selection

**Pending (Phases 5-7):**
- Phase 5: Drawing & annotation tools (freehand lines, arrows, angle tool, text)
- Phase 6: Side-by-side comparison view (two frames or two sessions)
- Phase 7: PDF report export

## Research Docs

Three PDF research docs in repo root (image-based PDFs):
- `9U Hitting Guide.pdf` (27 pages) — comprehensive hitting mechanics, drills, coaching philosophy
- `Assessment Form.pdf` (10 pages) — structured player evaluation: grip, stance, load, stride, connection, bat path, contact, finish, balance
- `Hitting Checklist.pdf` (10 pages) — phase-by-phase mechanics checklist with coaching tips and drills

Key concepts from docs referenced in @.claude/rules/swing-mechanics.md
