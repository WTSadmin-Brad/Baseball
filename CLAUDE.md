# Baseball Swing Analysis — AI Coaching App

## Behavioral Rules

Don't assume. Don't hide confusion. Surface tradeoffs.

Before implementing anything:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

Minimum code that solves the problem. Nothing speculative.
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Touch only what you must. Clean up only your own mess.
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- Every changed line should trace directly to the request.

Define success criteria. Loop until verified.
- Transform vague tasks into verifiable goals before starting.
- For multi-step tasks, state a brief plan with checkpoints.
- Strong success criteria let you work independently. Weak criteria require clarification — ask for it.

**These rules are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplplication, and clarifying questions come before implementation rather than after mistakes.

---

## Project Phase: Research & Pre-Planning

**We are NOT building production code right now.** We are in an extensive research phase to design the best possible AI-powered baseball coaching app before writing a single line of production code.

### What This Project Is
A youth baseball swing analysis tool being rethought from the ground up. The current app (Phases 1-4, ~2,200 lines) is a working prototype with MediaPipe pose detection, interactive markers, and metrics visualization. It may be thrown away entirely. The goal is to build something that provides MLB-level feedback and analysis accessible to every serious player and coach, using nothing more than a phone camera.

### Who It's For
- Primary: A youth travel ball coach tracking his step-son's multi-year development
- Secondary: The travel ball team's coaching staff
- Aspirational: Every travel ball parent, private instructor, and serious player

### The Decision Framework
Build the best possible tool for personal use first. If it's genuinely great, the product question answers itself later. Don't cut corners on analysis quality. Don't over-engineer infrastructure.

---

## Research Documents

All research artifacts live in `research/`. Read these before starting any research task:

| Document | Purpose |
|----------|---------|
| `research/01-current-state.md` | Complete inventory of the existing app — what's built, what's reusable |
| `research/02-vision-and-path.md` | Vision, user context, core philosophy, what success looks like |
| `research/03-landscape-analysis.md` | Competitors, open source ecosystem, Ryan Gunther's work, 10 feature ideas |
| `research/04-research-plan.md` | **Start here for task assignments.** Phased plan with specific deliverables. |

Research outputs go in `research/artifacts/`. Each artifact should be a self-contained document that another agent or session can read without needing prior conversation context.

---

## Domain Knowledge

### Swing Mechanics
See `.claude/rules/swing-mechanics.md` for detailed phase-by-phase mechanics compiled from coaching research PDFs. Key concepts:
- 8-phase swing sequence: Stance → Load → Launch → Swing → Connection → Contact → Finish
- "Tornado effect": ground-up sequencing (feet → hips → core → shoulders → hands)
- 7 tracked metrics: hip-shoulder separation, hip/shoulder rotation, elbow angles, knee angles, spine tilt

### Reference Materials (repo root)
- `9U Hitting Guide.pdf` (27 pages) — comprehensive hitting mechanics, drills, coaching philosophy
- `Assessment Form.pdf` (10 pages) — structured player evaluation checklist
- `Hitting Checklist.pdf` (10 pages) — phase-by-phase mechanics with coaching tips and drills

### Key External Resources
- [Driveline OpenBiomechanics](https://github.com/drivelineresearch/openbiomechanics) — largest open-source elite motion capture dataset (100 pitchers, 98 hitters)
- [pybaseball](https://github.com/jldbc/pybaseball) — Python library for Statcast, Baseball Reference, FanGraphs data
- [RyanGunther](https://github.com/RyanGunther) — MSc thesis on swing biomechanics, dimensionality reduction, SAM2 pipelines
- [Driveline: Bat Tracking & CV](https://www.drivelinebaseball.com/2025/02/bat-tracking-computer-vision-and-the-next-frontier/) — single-camera 3D bat reconstruction research

---

## Existing App (Reference Only)

The current prototype lives in `backend/` and `frontend/`. It is reference material, not the codebase we're building on. Key details for context:

**Backend** — FastAPI (Python)
- `main.py` — REST API: upload, pose detection, landmark editing, session management
- `pose_engine.py` — MediaPipe Pose (heavy model), metrics computation, annotated rendering
- `video_extract.py` — OpenCV video frame extraction
- `models.py` — Pydantic schemas

**Frontend** — React + Vite
- `FrameViewer.jsx` — Three-mode viewer (Annotated/Markers/Original) with Canvas drag editing
- `FrameCarousel.jsx`, `MetricsPanel.jsx`, `MetricsChart.jsx`, `UploadPanel.jsx`, `VideoFrameSelector.jsx`
- `useSession.js` — Hook managing all API calls and session state

**CLI** — `swing_analysis.py` (standalone reference script)

**Tech stack:** FastAPI, MediaPipe, OpenCV, React 19, Recharts, Vite
**Storage:** File-based sessions (JSON), no database
**Model:** MediaPipe Pose Landmarker Heavy (`pose_landmarker_heavy.task`, 30MB, downloaded separately)

---

## Agent Coordination

When working as part of a research team:

### Writing Research Artifacts
- Each artifact is a standalone markdown file in `research/artifacts/`
- Start with a one-paragraph summary of what was found and why it matters
- Include sources with URLs for everything cited
- End with a "Implications for Our Project" section — connect findings back to what we're building
- Be opinionated. "X is better than Y because Z" is more useful than "X and Y both have pros and cons"

### What NOT To Do During Research
- Don't write production code. Jupyter notebooks and throwaway scripts for proof-of-concepts are fine.
- Don't make architecture decisions prematurely. Document options and tradeoffs; decisions come in Phase 4.
- Don't install dependencies into the existing app.
- Don't modify files in `backend/` or `frontend/`.

### Artifact Quality Bar
Every research artifact should pass this test: "If a senior engineer read only this document, could they make an informed decision about the topic?" If not, it needs more depth or clearer conclusions.
