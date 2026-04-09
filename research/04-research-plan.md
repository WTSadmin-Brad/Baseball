# Research Plan

> Last updated: 2026-04-09

This document outlines a comprehensive research plan designed to be executed by a team of specialized Claude Code agents. Each phase produces concrete deliverables that feed into the next. The goal is to answer every critical question before writing a single line of production code.

---

## Research Philosophy

1. **Breadth before depth** — Survey everything first, then go deep on what matters
2. **Steal shamelessly, credit generously** — Build on existing open-source work
3. **Validate with data** — Don't assume; test against Driveline's dataset and real swings
4. **Think like the user** — Every technical decision must survive the question "does a travel ball coach care about this?"
5. **Document everything** — Research is only valuable if it's captured and retrievable

---

## Phase 1: Landscape & Technology Deep Dive

**Duration:** 1-2 weeks
**Goal:** Build a complete map of every relevant project, dataset, model, paper, and person in the baseball + CV + biomechanics space.

### Task 1.1: Open Source Project Catalog
Systematically catalog every relevant GitHub project. For each, document: what it does, tech stack, quality/maturity, license, last activity, what we can reuse.

**Search targets:**
- GitHub topics: `baseball`, `baseball-analytics`, `baseball-data`, `statcast`, `swing-analysis`, `pose-estimation`, `sports-biomechanics`, `motion-capture`, `bat-tracking`
- GitHub orgs: `drivelineresearch`, and any other baseball research orgs
- Individual repos already identified (see `03-landscape-analysis.md`)
- Adjacent sports CV projects (golf swing analysis, tennis, cricket) — same problems, different sport

**Deliverable:** `research/artifacts/open-source-catalog.md` — Organized table of every project with assessment of reusability.

### Task 1.2: Academic Paper Survey
Find and summarize key academic papers on:
- Pose estimation applied to sports (especially baseball)
- Markerless motion capture accuracy vs. marker-based
- Baseball swing biomechanics and performance predictors
- Single-camera 3D reconstruction techniques
- Bat/object tracking in sports video
- Dimensionality reduction for motion capture (Ryan Gunther's references + related work)

**Search targets:**
- Google Scholar, arXiv, ResearchGate
- References cited in Ryan Gunther's thesis repo
- Driveline's blog post references
- Theia's 50+ peer-reviewed validation studies

**Deliverable:** `research/artifacts/paper-survey.md` — Annotated bibliography with key findings and relevance to our project.

### Task 1.3: Deep Dive — Ryan Gunther's Work
Read and understand his actual code, not just the README. Specifically:
- `DimensionalityReductionBiomechData.R` — full pipeline walkthrough
- `dynamic_PPCA_pipeline.R` — how he separates signal from noise
- `feat_vec_LASSO.R` — feature selection for performance prediction
- `SAM2_isomap_pipeline.ipynb` — segmentation + manifold learning pipeline
- `SegmentationTraining09_2025.ipynb` — what model is he training?

**Questions to answer:**
- Can we replicate his dimensionality reduction in Python?
- What specific covariance structures predict bat speed/exit velo?
- How does his SAM2 pipeline improve on standard pose estimation?
- What's the minimum marker set needed for accurate swing reconstruction?

**Deliverable:** `research/artifacts/gunther-deep-dive.md` — Technical analysis with code snippets and translation notes.

### Task 1.4: Deep Dive — Driveline OpenBiomechanics Dataset
Download and explore the dataset. Understand:
- Data format (C3D files), how to load and process them
- What markers are tracked, sampling rate, data quality
- How hitting data is structured vs. pitching data
- What metadata is available (exit velo, bat speed, player info)
- How Ryan Gunther and others have processed this data

**Questions to answer:**
- Can we use this data to train/validate our own models?
- What's the relationship between specific biomechanical features and performance metrics?
- Can we build "archetype" swing profiles from this data?

**Deliverable:** `research/artifacts/openbiomechanics-analysis.md` — Dataset exploration report with code examples and key findings.

### Task 1.5: Deep Dive — Driveline Bat Tracking & Theia
Investigate the state of the art in bat tracking:
- Driveline's blog post on bat keypoint tracking methodology
- Their patent filing — what exactly did they patent?
- Theia's published validation studies and methodology
- Dylan Drummey's original bat keypoint work
- YOLO-based approaches for bat detection

**Questions to answer:**
- Is single-camera bat tracking feasible with current open-source models?
- What accuracy can we expect from phone video vs. high-speed cameras?
- What's the minimum viable approach for bat path estimation?

**Deliverable:** `research/artifacts/bat-tracking-feasibility.md` — Technical feasibility assessment with recommended approach.

### Task 1.6: Pose Estimation Model Comparison
Compare available pose estimation approaches for baseball specifically:
- MediaPipe Pose (current — heavy model, 33 landmarks)
- OpenPose (25 keypoints, used by Malter Analytics for MLB)
- YOLOv8-Pose (fast, good for real-time)
- MMPose / ViTPose (state-of-the-art accuracy)
- Custom fine-tuned models (trained on baseball-specific data)
- Apple Vision framework (if targeting iOS)

**Evaluation criteria:**
- Accuracy on baseball swings (occluded limbs, fast motion, bat in frame)
- Speed (real-time vs. batch processing)
- Landmark set (do we need more than 33 points? Hands/fingers?)
- Platform compatibility (on-device vs. cloud)

**Deliverable:** `research/artifacts/pose-model-comparison.md` — Head-to-head comparison with recommendations.

---

## Phase 2: User Research & Competitive Teardown

**Duration:** 1-2 weeks (can overlap with Phase 1)
**Goal:** Understand the actual users, their workflows, pain points, and what existing apps do well/poorly.

### Task 2.1: User Persona Development
Define 4-5 detailed user personas based on the people who would use this tool:
- **The Travel Ball Dad** — Records every cage session, wants to track son's progression
- **The Private Instructor** — 30-40 lessons/week, needs efficient analysis and parent communication
- **The Youth Coach** — Manages 12-15 players, needs team-level view
- **The High School Player** — Self-directed improvement, compares to peers
- **The Data-Obsessed Parent** — Wants every number, every trend, every comparison

For each: goals, frustrations, current tools, willingness to pay, technical sophistication, usage frequency.

**Deliverable:** `research/artifacts/user-personas.md`

### Task 2.2: Competitive App Teardown
For each major competitor, document:
- Complete feature list
- Pricing model
- Onboarding experience
- Analysis accuracy (test with our sample swings if possible)
- UX strengths and weaknesses
- App store rating + review analysis (especially 1-3 star reviews)
- What they're marketing vs. what they actually deliver

**Apps to analyze:**
- Mind & Muscle
- SwingPerfect
- b4-app
- Swing ML
- Blast Vision
- V1 Baseball
- OnForm
- Baseball AI (if available)
- WIN Reality SwingAI

**Deliverable:** `research/artifacts/competitive-teardown.md` — Feature matrix + detailed analysis of each app.

### Task 2.3: Community Research
Mine public forums and communities for user needs, complaints, and feature requests:
- Reddit: r/Homeplate, r/baseball, r/BaseballCoaching
- Twitter/X: baseball coaching, hitting mechanics discussions
- YouTube: popular hitting instruction channels and their methodologies
- Baseball forums: Discuss Baseball, HSBBW (High School Baseball Web)
- Facebook groups: travel ball parent groups

**Questions to answer:**
- What are coaches and parents actually asking for?
- What terminology do they use? (This informs our UI language)
- What's their relationship with technology? Trust level with AI?
- What would make them switch from their current approach?

**Deliverable:** `research/artifacts/community-research.md` — Synthesis of user needs from public sources.

### Task 2.4: Coaching Methodology Research
Survey the major hitting instruction philosophies and how they map to measurable mechanics:
- Driveline's data-driven approach
- Traditional "swing down" vs. modern launch angle philosophies
- Rotational vs. linear hitting theories
- Age-appropriate development progressions (what to teach at 8U vs. 12U vs. 14U)
- How professional hitting coaches structure their analysis

**Questions to answer:**
- Can the app support multiple coaching philosophies without being opinionated?
- What metrics matter at different age/skill levels?
- How do we avoid the app contradicting a player's coach?

**Deliverable:** `research/artifacts/coaching-methodology.md`

---

## Phase 3: Technical Proof-of-Concepts

**Duration:** 2-3 weeks
**Goal:** Answer the hardest technical questions with small, focused experiments before committing to an architecture.

### Task 3.1: Pose Estimation Accuracy Benchmark
Using our existing sample images (8 swing frames) + additional test images:
- Run MediaPipe heavy (our current approach)
- Run at least 2 alternative models
- Compare landmark accuracy (manually annotated ground truth)
- Test with different camera angles, lighting conditions, backgrounds
- Measure inference speed on different hardware

**Deliverable:** `research/artifacts/pose-benchmark/` — Benchmark results, comparison images, recommendation.

### Task 3.2: Bat Detection Spike
Can we detect and track the bat from phone video?
- Try YOLO-based object detection for bat bounding box
- Try keypoint detection for bat cap + knob
- Test on our sample images and any publicly available batting video
- Measure accuracy, discuss what's needed for training a custom model

**Deliverable:** `research/artifacts/bat-detection-spike/` — Results, sample outputs, feasibility assessment.

### Task 3.3: Swing Fingerprinting Prototype
Translate Ryan Gunther's R-based dimensionality reduction approach to Python:
- Load Driveline OpenBiomechanics hitting data
- Implement PCA/PPCA on marker trajectories
- Attempt swing clustering and similarity scoring
- Validate against exit velocity / bat speed metadata

**Deliverable:** `research/artifacts/swing-fingerprinting/` — Jupyter notebook with results.

### Task 3.4: LLM Coaching Feedback Prototype
Test Claude/GPT for generating coaching feedback from swing metrics:
- Input: metrics JSON from our current app + player context (age, level)
- Output: natural language coaching feedback with drill recommendations
- Evaluate: accuracy, tone, age-appropriateness, actionability
- Test: can it reference our coaching PDFs for drill recommendations?
- Consider: prompt engineering vs. fine-tuning vs. RAG approaches

**Deliverable:** `research/artifacts/llm-coaching-prototype/` — Example prompts, outputs, evaluation.

### Task 3.5: Temporal Comparison Spike
Test Dynamic Time Warping for swing comparison:
- Take multiple swings from same player (different sessions)
- Align using DTW
- Visualize differences
- Test with swings from different players

**Deliverable:** `research/artifacts/temporal-comparison/` — Visualization outputs, feasibility notes.

### Task 3.6: Mobile/On-Device Feasibility
What can run on a phone vs. what needs cloud?
- Test MediaPipe on-device (already works in browsers/mobile)
- Test lighter pose models (YOLO-Pose, MoveNet) for real-time use
- Benchmark inference times on typical phone hardware
- Assess: on-device for capture + pose, cloud for deep analysis?

**Deliverable:** `research/artifacts/mobile-feasibility.md`

---

## Phase 4: Architecture & Vision Synthesis

**Duration:** 1 week
**Goal:** Synthesize all research into a definitive architecture document and product vision.

### Task 4.1: Architecture Decision Records
For each major technical decision, document the options considered, tradeoffs, and recommendation:
- Pose estimation model selection
- On-device vs. cloud processing split
- Database choice (player profiles, session history)
- Frontend framework and platform (web, native, React Native, Flutter)
- AI/LLM integration approach (API calls vs. on-device vs. RAG)
- Storage architecture (media files, analysis data, user data)
- API design (REST vs. GraphQL, real-time vs. batch)

**Deliverable:** `research/artifacts/architecture-decisions.md`

### Task 4.2: Feature Prioritization Matrix
Map all feature ideas against:
- User impact (from persona research)
- Technical feasibility (from proof-of-concepts)
- Development effort
- Differentiation value (what makes us unique vs. competitors)

Produce a prioritized roadmap: MVP → V1 → V2 → Future.

**Deliverable:** `research/artifacts/feature-prioritization.md`

### Task 4.3: "Press Release from the Future"
Amazon-style working backwards document. Write the review that appears in a baseball magazine 2 years from now. What does it say? This forces clarity on the 3 things the app does better than anything else.

**Deliverable:** `research/artifacts/press-release.md`

### Task 4.4: Final Vision Document
Synthesize everything into a single, definitive document:
- The problem we're solving
- Who we're solving it for
- The 3 core differentiators
- Technical architecture overview
- MVP feature set
- Development roadmap
- Open questions and risks

**Deliverable:** `research/artifacts/vision-document.md`

---

## Agent Team Structure

These research tasks are designed to be delegated to specialized Claude Code agents. Recommended team structure:

### Agent 1: Technical Scout
**Scope:** Tasks 1.1, 1.2, 1.5, 1.6
**Skills:** GitHub exploration, paper reading, technical comparison
**Instructions:** Catalog everything. Be exhaustive. Quality of assessment matters more than quantity of projects found. For each project, answer: "What can we steal?"

### Agent 2: Deep Dive Analyst
**Scope:** Tasks 1.3, 1.4, 3.3
**Skills:** Code reading (R and Python), data analysis, statistical methods
**Instructions:** Read the actual code, not just the READMEs. Translate R to Python concepts. Focus on what's mathematically sound vs. what's just interesting.

### Agent 3: User & Market Researcher
**Scope:** Tasks 2.1, 2.2, 2.3, 2.4
**Skills:** Web research, app analysis, community mining, synthesis
**Instructions:** Think like a product manager. Numbers matter less than insights. "Users complain about X" is less useful than "Users complain about X because Y, which means we should Z."

### Agent 4: Prototype Builder
**Scope:** Tasks 3.1, 3.2, 3.4, 3.5, 3.6
**Skills:** Python, ML/CV libraries, prototyping, benchmarking
**Instructions:** Build the smallest possible thing that answers the question. No production code. Jupyter notebooks are fine. Focus on "can we?" not "how should we ship it?"

### Agent 5: Architect / Synthesizer
**Scope:** Tasks 4.1, 4.2, 4.3, 4.4
**Skills:** System design, technical writing, product thinking
**Instructions:** You've read everything the other agents produced. Now make the hard calls. What do we build, in what order, with what technology? Be opinionated.

---

## Key Questions This Research Must Answer

Before we write production code, we need confident answers to these:

### Technical
1. What pose estimation model gives us the best accuracy on baseball swings from phone video?
2. Can we track a bat from single-camera phone video with useful accuracy?
3. Can we run pose estimation on-device (phone/browser) or does it require cloud processing?
4. What's the minimum viable approach for 3D reconstruction from a single camera?
5. Can LLM-generated coaching feedback be accurate and age-appropriate enough to trust?

### Product
6. Who is our primary user and what does their workflow look like today?
7. What are the 3 features that would make someone switch from their current app?
8. What's the right pricing model (if we go product)?
9. How do we handle the "my coach says something different" problem?
10. What privacy and safety considerations exist for an app used with minors?

### Data & Science
11. Which biomechanical metrics actually predict hitting performance?
12. Can we build meaningful "swing archetypes" from the Driveline dataset?
13. How much data do we need per player for meaningful trend analysis?
14. What's the accuracy threshold where AI feedback becomes trustworthy?

### Business
15. What's the competitive moat — what's hard to replicate?
16. Is this a standalone app or a platform (API for other coaches/apps)?
17. What partnerships would accelerate development (Driveline, equipment companies)?

---

## Directory Structure for Research Artifacts

```
research/
├── 01-current-state.md          ← You are here
├── 02-vision-and-path.md
├── 03-landscape-analysis.md
├── 04-research-plan.md           ← This document
└── artifacts/
    ├── open-source-catalog.md
    ├── paper-survey.md
    ├── gunther-deep-dive.md
    ├── openbiomechanics-analysis.md
    ├── bat-tracking-feasibility.md
    ├── pose-model-comparison.md
    ├── user-personas.md
    ├── competitive-teardown.md
    ├── community-research.md
    ├── coaching-methodology.md
    ├── architecture-decisions.md
    ├── feature-prioritization.md
    ├── press-release.md
    ├── vision-document.md
    ├── pose-benchmark/
    ├── bat-detection-spike/
    ├── swing-fingerprinting/
    ├── llm-coaching-prototype/
    ├── temporal-comparison/
    └── mobile-feasibility.md
```

---

## Success Criteria

This research phase is complete when:
- [ ] We can name our pose estimation model with confidence and data backing the choice
- [ ] We know whether bat tracking from phone video is feasible (and if so, what approach)
- [ ] We have a validated set of metrics that actually predict swing quality
- [ ] We have a feature-prioritized MVP definition
- [ ] We know our primary user persona and their top 3 needs
- [ ] We have an architecture that supports the MVP + clear path to future features
- [ ] We can articulate in one sentence what makes this app different from everything else
