# Research Recovery — Phase 1 Tasks 1.1 & 1.3

> **Status:** Temporary. Delete this entire `_recovery/` directory once the final artifacts (`research/artifacts/open-source-catalog.md` and `research/artifacts/gunther-deep-dive.md`) are written and verified.

## Why This Exists

Background research agents spawned for Phase 1 Tasks 1.1 (Open Source Catalog) and 1.3 (Ryan Gunther Deep Dive) successfully gathered comprehensive research via WebSearch + WebFetch but timed out or hit plan-mode blocks before they could write their final artifacts. Their tool-result outputs (the actual web content fetched) were captured from agent logs and extracted here so a fresh session can synthesize the artifacts without having to repeat the web research (which is what caused every timeout).

## Files

| File | Size | Contents |
|------|------|----------|
| `gunther-research-raw.txt` | ~120KB | Full source code of every R script and Jupyter notebook in Ryan Gunther's GitHub repos (`Masters-Thesis-Baseball-Biomech-Data` and `Computer-Vision-Baseball-Academic-`), plus academic paper summaries (Liu 2006, Barbic 2004, Blackburn & Ribeiro 2007), plus OpenBiomechanics dataset marker-set documentation. Format: sequential CALL/RESULT blocks from the agent log. |
| `catalog-research-agent1-raw.txt` | ~230KB | Tool outputs from the first catalog agent. Includes WebFetch results for ~40 GitHub repos (stars, license, last commit, description, techniques) and WebSearch results across ~20 topic areas. Most thorough single source. |
| `catalog-research-agent3-raw.txt` | ~170KB | Tool outputs from the second catalog agent (re-run after the first one hit plan mode). Mostly overlaps with agent 1, but adds unique data for: `py-c3d`, `mlbgame`, `dtw-python`, `opensim-core`, `dtaidistance`, `ezc3d`, `AthletePose3D`, `sam2` (direct repo), `google-ai-edge/mediapipe` (the current active mirror). |

## Format Notes

Each file is plain text with `=== ... ===` separator blocks. Every block is one tool call with its result:

```
================================================================================
[N] CALL: WebFetch <url>     OR    WebSearch <query>
================================================================================
<full response text>
```

Warning: some lines are very long (up to 18,000 characters) because tool responses are captured as single lines in the original JSONL logs. Use offset/limit when reading with the Read tool, or `Grep` for specific strings.

## What To Do Next

A new session should:

1. **Read the context docs first** (required):
   - `CLAUDE.md` (project instructions, behavioral rules, research phase status)
   - `research/01-current-state.md`
   - `research/02-vision-and-path.md`
   - `research/03-landscape-analysis.md`
   - `research/04-research-plan.md` (section Task 1.1 and Task 1.3 specify deliverable format and questions to answer)

2. **Read the recovery files** to understand what was found. For the catalog agent files, the most efficient approach is:
   - First `Grep -n` for `CALL:` to get a line-number index of all fetches/searches
   - Then `Read` with `offset`/`limit` to jump to specific blocks of interest

3. **Write the two artifacts** directly using the `Write` tool:
   - `research/artifacts/open-source-catalog.md` — from `catalog-research-agent1-raw.txt` + `catalog-research-agent3-raw.txt`
   - `research/artifacts/gunther-deep-dive.md` — from `gunther-research-raw.txt`

4. **Do NOT do additional web research** unless a specific gap is identified. The recovered files contain enough data for both artifacts. Additional searches were the direct cause of every prior timeout.

5. **Write each artifact in a single `Write` tool call.** Do not do it in pieces with Edit — the whole-document Write is what failed to execute fast enough in prior attempts, so be prepared: one focused Write per doc, nothing else happening during it.

6. **After both artifacts exist and are reviewed**, delete this entire `_recovery/` directory in the same commit that finalizes the artifacts, or in a follow-up cleanup commit.

## Artifact Requirements (from CLAUDE.md)

Both artifacts must:
- Start with a one-paragraph summary of what was found and why it matters
- Include sources with URLs for everything cited
- End with an "Implications for Our Project" section
- Be opinionated ("X is better than Y because Z")
- Pass the test: "If a senior engineer read only this document, could they make an informed decision about the topic?"

## Key Findings Already Confirmed

**Task 1.1 — Open Source Catalog** (catalog-research-agent1-raw.txt has full data):
- ~50 relevant projects across 8 categories
- Highest-value reusable: `pybaseball`, `OpenBiomechanics`, `BaseballCV` (archived but has trained YOLO bat/ball models), `Pose2Sim`, `rtmlib`, `GolfDB/SwingNet`, `roboflow/supervision`, `SAM2`, `WHAM`
- Critical gap identified: **no open-source project does phone-camera baseball swing analysis with MLB-level biomechanical feedback**. Closest work is golf-focused (GolfDB, Pose2Par), multi-camera (Pose2Sim), or data-only (OpenBiomechanics).

**Task 1.3 — Ryan Gunther Deep Dive** (gunther-research-raw.txt has full data):
- Full source code was retrieved for `DimensionalityReductionBiomechData.R`, `dynamic_PPCA_pipeline.R`, `feat_vec_LASSO.R`, `SAM2_isomap_pipeline.ipynb`, `SegmentationTraining09_2025.ipynb`, and all supporting scripts
- His pipeline: PCA → PFA (via k-means on |eigenvectors|) → reduces 165 features (55 markers × 3 axes) to **6 principal markers = 18 dims** → sliding-window PPCA with Mahalanobis distance for segment detection → divisive k-means clustering of segment covariance feature vectors (171-dim upper triangle) → LASSO via glmnet to predict exit velo / bat speed
- **Author's own conclusion (from his R comments)**: "fv's not useful for predicting exit velo but there are other factors at play like contact quality...biggest takeaway is that there are more efficient and less efficient ways to move, which are captured in the covariance structure of a dimensionality-reduced dataset"
- The 6 principal markers found: Marker5, RWRA, RMKNE, LANK, LASI, Marker4 (i.e., right wrist, right inner knee, left ankle, front of left hip, and two bat markers) — consistent with biomechanical intuition
- SAM2 pipeline: yt-dlp → manual click prompting → SAM2 video segmentation → distance-transform magma overlay → flatten silhouettes → Isomap 2D manifold → DTW for swing comparison (inspired by Blackburn & Ribeiro 2007)
- Academic references traced: Liu et al. 2006 "Human motion estimation from a reduced marker set", Barbic et al. 2004 "Segmenting Motion Capture Data into Distinct Behaviors", Blackburn & Ribeiro 2007 "Human Motion Recognition Using Isomap and Dynamic Time Warping"
