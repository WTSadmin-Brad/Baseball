# Landscape Analysis: Market, Technical & Open Source

> Last updated: 2026-04-09

---

## Key People & Projects to Learn From

### Ryan Gunther (GitHub: RyanGunther)
**Who:** MSc Statistics student at Brock University, thesis on baseball swing biomechanics.

**Repos:**
| Repository | Focus | Key Tech |
|-----------|-------|----------|
| `Masters-Thesis-Baseball-Biomech-Data` | Dimensionality reduction on Driveline motion capture data | R, PCA, PPCA, K-means, covariance segmentation |
| `Computer-Vision-Baseball-Academic-` | CV pipeline for thesis: segmentation → manifold learning | SAM2, Isomap, YOLOv8, distance transforms |
| `Computer-Vision-Baseball-Independent-Research-` | Independent ball tracking + pose estimation | (Empty repo — work in progress) |
| `Computational-Statistics-Scripts` | Graduate ML coursework | R, ML algorithms |
| `Neural-Nets-from-Statquest-Book` | Neural network fundamentals | Jupyter, Python |

**What's Valuable:**
- His thesis proves you can identify **statistical signatures of swing quality** from motion capture data using dimensionality reduction
- Key finding: certain body-part covariance structures correlate with bat speed and exit velocity
- His use of Driveline's OpenBiomechanics dataset shows how to work with elite-level biomechanical data
- His SAM2 + Isomap pipeline represents a cutting-edge approach to body segmentation and pose manifold analysis
- References: Liu et al. (2006) "Human motion estimation from a reduced marker set," Barbic et al. (2004) "Segmenting Motion Capture Data into Distinct Behaviors"

**Where He Fits in the Puzzle:**
Ryan represents the **statistical/academic corner** — strong on "what does the data say?" but not building consumer tools. His work answers "which marker covariances predict exit velocity?" — gold for an intelligent analysis engine, but raw research that needs a coaching translation layer and UX to reach actual players and coaches.

**How to Piggyback:**
- Study his dimensionality reduction pipeline for swing fingerprinting
- Use his methodology for validating our own metrics against performance outcomes
- His SAM2 segmentation approach could improve body isolation in cluttered cage/field backgrounds
- His academic references are a reading list for the underlying science

### Other Key People/Projects to Investigate

| Person/Project | Why They Matter | URL |
|---------------|-----------------|-----|
| **Driveline Research Team** | OpenBiomechanics dataset, bat tracking patent, Theia partnership | [github.com/drivelineresearch](https://github.com/drivelineresearch) |
| **Dylan Drummey** | Pioneered bat keypoint tracking with MLB video (inspired Driveline's CV work) | Research referenced in Driveline blog |
| **natekbackman (Baseball-Cinematography)** | Dynamic Time Warping for pitcher mechanics comparison | [github.com/natekbackman/Baseball-Cinematography](https://github.com/natekbackman/Baseball-Cinematography) |
| **Malter Analytics** | OpenPose applied to MLB broadcast video for mechanics comparison | [malteranalytics.github.io/mlb-openpose](https://malteranalytics.github.io/mlb-openpose) |
| **jldbc (pybaseball)** | Python library for Statcast, Baseball Reference, FanGraphs data | [github.com/jldbc/pybaseball](https://github.com/jldbc/pybaseball) |
| **anishreddy3** | TensorFlow + OpenPose for real-time pitcher pose estimation | [github.com/anishreddy3/tf-openpose-baseball-pitcher](https://github.com/anishreddy3/tf-openpose-baseball-pitcher) |
| **pascalewalters** | Baseball tracking (ball + player) | [github.com/pascalewalters/baseball-tracking](https://github.com/pascalewalters/baseball-tracking) |
| **Strojove-uceni** | Pose estimation for swing improvement (academic) | [github.com/Strojove-uceni/23206-final-pose-estimation-for-swing-improvement](https://github.com/Strojove-uceni/23206-final-pose-estimation-for-swing-improvement) |

---

## Competitive Landscape

### Tier 1 — Lab-Grade (Inaccessible to consumers)

**Theia3D**
- World's first markerless bat + body tracking using deep learning
- Multi-camera high-speed video, no sensors or markers needed
- Validated by Driveline and PLNU Biomechanics Lab, 50+ peer-reviewed studies
- Used by NBA, Olympic Training Center, MLB organizations
- Captures: 3D bat path, speed, attack angle, contact point, full-body kinematics, joint sequencing
- **Limitation:** Requires multi-camera setup, not consumer-accessible
- [theiamarkerless.com](https://www.theiamarkerless.com/bat-tracking)

**Driveline Internal Tools**
- Filed US patent on using the bat itself as a calibration object for single-camera 3D reconstruction
- Partnership with Theia for markerless tracking at scale
- Collect synchronized bat-and-body data from real swings without sensors
- **Limitation:** Proprietary, facility-only
- [drivelinebaseball.com](https://www.drivelinebaseball.com/2025/02/bat-tracking-computer-vision-and-the-next-frontier/)

### Tier 2 — Hardware-Dependent ($150-$300+)

**Blast Motion**
- Bat-mounted sensor, most accurate bat speed and attack angle data
- Auto-edited video clips, green/yellow/red scoring system
- Good for serious HS/college players willing to invest
- **Pros:** Precise bat metrics, automatic swing detection
- **Cons:** Misses full body mechanics, sensor cost + subscription, only measures bat not body
- [blastmotion.com](https://blastmotion.com/products/baseball/)

**HitTrax / Rapsodo**
- Facility-based systems, $5K-$15K+
- Ball flight tracking, exit velo, launch angle, spray charts
- **Pros:** Gold standard ball flight data
- **Cons:** Facility-only, expensive, no body mechanics analysis

### Tier 3 — Phone-Based AI Apps (Our competitive space)

**Mind & Muscle** (~$10/mo)
- AI video analysis from phone video, no hardware
- Includes pitching analysis, mental training, game IQ tools
- Team management features
- **Pros:** All-in-one, affordable, no hardware
- **Cons:** Generalist approach, less depth on swing mechanics specifically

**SwingPerfect** (Free + IAP)
- AI-powered exit velocity, launch angle, biomechanics from video
- Displays body part mechanics during swing
- **Pros:** No hardware needed, visual biomechanics display
- **Cons:** Accuracy concerns, limited coaching translation

**b4-app** (Subscription)
- Bat Contact Point (BCP) technology
- Exit velocity, launch angle, bat path, biomechanics
- **Pros:** Innovative contact point tracking
- **Cons:** Inaccurate exit velocity readings reported, poor customer support response times

**Swing ML** (Paid)
- Machine learning swing analysis
- **Pros:** Good graphics, user-friendly
- **Cons:** Frequent failure to capture video, "move to center" errors, unreliable

**V1 Baseball / OnForm** (Subscription)
- Video annotation and coach-player sharing platforms
- Drawing tools, slow motion, comparison views
- **Pros:** Good for coach-player communication
- **Cons:** Less AI analysis, more manual annotation tool

### Common Complaints Across Tier 3 (from app store reviews, forums)
1. **Inaccurate readings** — exit velo, launch angle often wrong
2. **Failure to capture** — app doesn't detect the swing or loses tracking
3. **Numbers without advice** — tells you what's wrong but not how to fix it
4. **Poor support** — emails go unanswered
5. **Subscription fatigue** — another $10/mo for something that sort of works
6. **No historical tracking** — can't see progression over time
7. **One-size-fits-all** — no age/level adjustment in feedback
8. **Camera position sensitivity** — only works from specific angles

**The gap:** Every app either gives you numbers (without coaching context) or gives you coaching (without data backing). Nobody bridges the two well.

---

## Open Source Ecosystem — Building Blocks

### Datasets

**Driveline OpenBiomechanics Project**
- Largest open-source elite-level motion capture dataset in baseball
- 100 pitchers, 98 hitters
- 47 body markers + 10 bat markers per swing
- Raw C3D files + processed biomechanics data
- 100% free for individual use
- [github.com/drivelineresearch/openbiomechanics](https://github.com/drivelineresearch/openbiomechanics)
- [openbiomechanics.org](https://www.openbiomechanics.org/)

**Statcast (via pybaseball)**
- Pitch-level data: perceived velocity, spin rate, exit velocity, coordinates
- Available from 2008-present
- Player-level and game-level queries
- [github.com/jldbc/pybaseball](https://github.com/jldbc/pybaseball)

### Models & Libraries

| Tool | What It Does | Relevance |
|------|-------------|-----------|
| MediaPipe Pose | 33-landmark body detection | Current app uses this; baseline to beat |
| SAM2 (Segment Anything 2) | Instance segmentation | Body isolation in cluttered backgrounds |
| YOLOv8 | Object detection + keypoint estimation | Bat tracking, player detection |
| OpenPose | 25-keypoint body detection | Alternative to MediaPipe, used in MLB research |
| Dynamic Time Warping | Time-series alignment | Swing comparison across different timing |
| PPCA / PCA | Dimensionality reduction | Swing fingerprinting (Ryan Gunther's approach) |

### Key Technical Breakthroughs to Study

1. **Driveline's single-camera 3D bat reconstruction** — Using the bat as a calibration object (known length) to reconstruct 3D trajectory from 2D video. Patent filed 2024.

2. **Theia's deep learning markerless tracking** — Multi-camera to 3D without markers, trained on millions of human movement data points. Shows what's possible with enough training data.

3. **SAM2 for sports segmentation** — Ryan Gunther's use of Meta's latest segmentation model for baseball-specific body isolation. Combined with Isomap for manifold learning.

4. **Bat keypoint detection** — Dylan Drummey's work on detecting bat cap and knob points, enabling bat path and speed estimation from standard video.

---

## 10 High-Level Feature Ideas

### 1. Swing DNA / Fingerprinting
Use dimensionality reduction (Ryan Gunther's approach) to create a statistical signature of each player's swing. Track how it evolves. Detect regression, fatigue, or mechanical drift. Compare to archetypes of successful hitters at the same level.

### 2. Coaching Translation Layer
The missing piece in every app. Pipeline: raw metrics → age/level-appropriate coaching cues → specific drills with video demonstrations. This is where an LLM becomes transformative — generating natural language coaching feedback that sounds like a great hitting instructor, not a data scientist.

### 3. Temporal Swing Comparison
Synchronized, time-warped overlays of the same player's swing across different dates. Dynamic Time Warping (from Baseball-Cinematography project) enables comparison even when swing timing differs. "Here's March vs. June — your load timing improved but you're losing separation at contact."

### 4. Single-Camera 3D Reconstruction
Driveline proved this works using the bat as a calibration object. Even approximate 3D from phone video would leapfrog every Tier 3 app. Hard technical problem but research exists.

### 5. Progressive Development Tracking
Longitudinal player profiles across an entire season (or years). Detect trends, plateaus, regressions. "Compared to last month, your swing sequencing improved 15% but your bat path is getting steeper." No consumer app does this well.

### 6. Pitch-Situational Analysis
Integrate Statcast data. "You're pulling off on outside pitches. Here's what your swing looks like on inside vs. outside vs. middle." Tie the swing to the context of what's being thrown.

### 7. AI Practice Planner
Based on detected weaknesses, generate a structured practice plan. "This week: 50 tee reps focusing on staying connected (drill video), 30 front toss reps focusing on opposite field, film 5 swings Friday for re-analysis."

### 8. Social / Community Layer
Baseball parents and coaches are obsessive sharers. Shareable swing reports, coach-to-parent communication, team-level analytics. Think Strava for swings. Handle carefully for youth privacy.

### 9. Bat Tracking from Phone Video
The holy grail for consumer apps. YOLO-based keypoint detection on bat cap and knob from single camera. Even 80% accuracy for bat path and speed estimation would be a game-changer.

### 10. The "Film Room" Experience
Democratize what MLB teams have. Side-by-side comparison with pro swing archetypes (properly anonymized/licensed). "Your load looks like this. Here's how [archetype] loads. Here's the difference." Scouting-level analysis for everyone.

---

## The Opportunity Gap

No single app or project combines all of these:
- **Computer Vision** (body pose + bat tracking + ball tracking from phone video)
- **Biomechanical Science** (validated metrics that actually predict performance)
- **Coaching Intelligence** (translating data into teaching, age-appropriate)
- **Longitudinal Tracking** (player development over months/years)
- **Great UX** (coach-friendly, not data-scientist-friendly)
- **AI/LLM Layer** (natural language feedback, practice planning, contextual analysis)
- **Accessibility** (phone camera only, affordable, no hardware)

Each competitor does 1-2 of these. Nobody does all of them. That's the opportunity.
