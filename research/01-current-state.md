# Current State Assessment

> Last updated: 2026-04-09

## Overview

A youth baseball swing analysis tool with automatic pose detection, interactive marker editing, and swing metrics tracking. Full-stack web application: FastAPI backend (Python) + React frontend (Vite). Approximately **2,200 lines of code** across backend and frontend.

The app is functional through **Phase 4** of a 7-phase roadmap. It processes an 8-frame swing sequence, detects body landmarks via MediaPipe, computes biomechanical metrics, and provides an interactive viewer with draggable markers and charts.

---

## Architecture

```
Baseball/
├── backend/
│   ├── main.py           (354 lines) — FastAPI REST API, session management, file serving
│   ├── pose_engine.py    (343 lines) — MediaPipe Pose detection, metrics computation, annotated rendering
│   ├── video_extract.py  (76 lines)  — OpenCV video frame extraction + thumbnails
│   ├── models.py         (37 lines)  — Pydantic request/response schemas
│   └── __init__.py
├── frontend/
│   └── src/
│       ├── App.jsx              (121 lines) — Main layout, view mode state
│       ├── main.jsx             (10 lines)  — Entry point
│       ├── hooks/
│       │   └── useSession.js    (113 lines) — All API calls and session state
│       └── components/
│           ├── FrameViewer.jsx         (287 lines) — Three-mode viewer (Annotated/Markers/Original)
│           ├── FrameCarousel.jsx       (36 lines)  — Thumbnail strip navigation
│           ├── MetricsPanel.jsx        (69 lines)  — Color-coded angle readouts
│           ├── MetricsChart.jsx        (71 lines)  — Recharts line chart across phases
│           ├── UploadPanel.jsx         (51 lines)  — Drag-and-drop upload
│           └── VideoFrameSelector.jsx  (79 lines)  — Pick key frames from video
├── swing_analysis.py     (560 lines) — Original CLI script (standalone, reference only)
├── requirements.txt
├── CLAUDE.md
├── .claude/rules/
│   ├── swing-mechanics.md  — Domain knowledge compiled from coaching PDFs
│   └── frontend.md         — Frontend patterns and conventions
├── annotated/              — CLI output: 8 annotated JPEGs + composite grid + metrics JSON
├── sessions/               — Runtime: file-based session storage (created on first upload)
├── IMG_0766-0773.jpeg      — 8 sample swing images
├── 9U Hitting Guide.pdf    — 27-page coaching reference
├── Assessment Form.pdf     — 10-page player evaluation checklist
└── Hitting Checklist.pdf   — 10-page phase-by-phase mechanics checklist
```

## Tech Stack

### Backend
| Dependency | Version | Purpose |
|-----------|---------|---------|
| FastAPI | 0.115.0 | REST API framework |
| Uvicorn | 0.30.6 | ASGI server |
| python-multipart | 0.0.9 | File upload handling |
| opencv-python-headless | latest | Image/video processing |
| mediapipe | latest | Pose landmark detection (heavy model) |
| numpy | latest | Numerical computation |
| Pillow | latest | Image manipulation |

### Frontend
| Dependency | Version | Purpose |
|-----------|---------|---------|
| React | 19.2.4 | UI framework |
| Recharts | 3.8.1 | Charts/visualization |
| Vite | 8.0.4 | Build tool / dev server |

### External Model
- **MediaPipe Pose Landmarker Heavy** (`pose_landmarker_heavy.task`, 30MB) — downloaded separately, not in repo

---

## Features — What's Working

### Image/Video Upload
- Drag-and-drop or file picker for images (multiple JPEGs) or video
- Video upload extracts frames at ~10fps, presents grid for user to pick up to 8 key frames
- Images stored in session directory

### Pose Detection
- MediaPipe heavy model detects 33 body landmarks per frame
- Landmarks stored as normalized [0,1] coordinates
- Runs on all frames in sequence after upload

### Metrics Computation
8 metrics computed from landmark positions:
| Metric | What It Measures |
|--------|-----------------|
| Hip-Shoulder Separation | Sequencing quality (hips leading shoulders) |
| Hip Line Angle | Hip rotation from horizontal |
| Shoulder Line Angle | Shoulder rotation from horizontal |
| Back Elbow Angle | Connection/slot position |
| Front Elbow Angle | Lead arm extension |
| Front Knee Angle | Front side firmness/blocking |
| Back Knee Angle | Back leg drive |
| Spine Tilt | Posture maintenance |

### Annotated Frame Rendering
- Server-side rendering: skeletal overlay with color-coded connections, joint markers, metrics panel, plumb line
- Color palette: Cyan (shoulders), Orange (hips), White (spine), Green (arms), Yellow (legs)

### Interactive Marker Editing
- Canvas overlay mode with draggable landmarks
- Hit detection, drag-to-reposition any of 33 landmarks
- Save triggers backend recomputation of all metrics
- Reset to original detection

### Visualization
- Metrics panel: color-coded angle readouts per frame
- Line chart: 4 key metrics plotted across all 8 swing phases
- Active frame highlight on chart

### 8-Phase Swing Framework
Frames mapped to phases: Stance/Setup → Early Load → Load/Stride → Launch Position → Swing Initiation → Connection/Approach → Contact/Extension → Follow-Through/Finish

### Session Management
- File-based (JSON state files in `sessions/` directory)
- No database, no auth — single-user local tool
- Persists landmarks, metrics, annotations per frame

---

## Features — What's Pending

### Phase 5: Drawing & Annotation Tools
- Freehand lines, arrows, angle measurement tool, text labels
- Backend endpoint exists (`PUT /api/annotations`) but is a stub
- No frontend drawing implementation

### Phase 6: Side-by-Side Comparison
- Compare two frames from same session or across sessions
- No implementation started

### Phase 7: PDF Report Export
- Generate shareable swing analysis reports
- No implementation started

---

## Reusability Assessment

### Likely Reusable
- **Domain knowledge** (`.claude/rules/swing-mechanics.md`) — comprehensive, well-structured, source-referenced
- **Research PDFs** — coaching content is timeless
- **8-phase swing framework** — solid pedagogical foundation
- **Color palette and visualization conventions** — well-chosen, consistent
- **Metrics computation logic** — the math in `pose_engine.py:compute_metrics()` is correct and transferable
- **Sample images** — useful for testing

### Likely Replaced in a Rebuild
- **MediaPipe as sole pose engine** — may want to fine-tune or use more advanced models (SAM2, custom YOLO, etc.)
- **File-based session storage** — won't scale; needs a real database for multi-user, historical tracking
- **Frontend architecture** — inline styles, no design system, no state management beyond a single hook
- **Backend architecture** — monolithic FastAPI; a larger app needs service separation (auth, analysis, storage, AI)
- **No bat tracking** — current system only tracks body; bat is a critical missing piece
- **No player profiles or historical tracking** — sessions are isolated, no longitudinal analysis
- **No AI/LLM integration** — no natural language coaching feedback, no drill recommendations

### Key Gaps vs. the Vision
1. No player identity or progression tracking
2. No bat detection or tracking
3. No ball tracking or pitch context
4. No coaching translation layer (metrics → actionable advice)
5. No comparison tools
6. No team/multi-player management
7. No mobile-first design
8. No cloud infrastructure
9. No export/sharing capabilities
10. No integration with external data sources (Statcast, etc.)

---

## How to Run (Reference)

```bash
# Setup
pip install -r requirements.txt
cd frontend && npm install && npx vite build && cd ..
python3 -c "import urllib.request; urllib.request.urlretrieve('https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/pose_landmarker_heavy.task', 'pose_landmarker_heavy.task')"

# Production
uvicorn backend.main:app --port 8000

# Development
# Terminal 1: uvicorn backend.main:app --reload --port 8000
# Terminal 2: cd frontend && npm run dev
```
