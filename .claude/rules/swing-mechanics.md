---
paths:
  - "backend/pose_engine.py"
  - "swing_analysis.py"
  - "frontend/src/components/MetricsPanel.jsx"
  - "frontend/src/components/MetricsChart.jsx"
  - "frontend/src/components/FrameViewer.jsx"
---

# Swing Mechanics Domain Knowledge

Compiled from 9U Hitting Guide, Assessment Form, and Hitting Checklist PDFs.
This knowledge informs how pose markers are placed, which angles matter, and what "good" looks like at each phase.

## The Swing Sequence (Ground Up)

The swing works from the ground up ("tornado effect"):
1. Heel plant triggers hips
2. Hips fire and rotate (belt buckle toward pitcher)
3. Core stretches (hip-shoulder separation builds)
4. Shoulders follow, hands stay back
5. Hands deliver barrel on short path inside the ball
6. Extension through contact
7. Balanced finish

**Lower half must lead upper half.** If hands go early, it's "out of sequence" — a common youth issue.

## Phase-by-Phase Checkpoints

### Stance / Setup
- Athletic position, feet about bat's length apart
- Grip: fingertips not palms, door-knocking knuckles aligned
- Correct distance from plate (front arm reaches outside corner with bat)
- Weight balanced, slight flex in knees

### Load & Stride
- Smooth rhythm, not static — "imagine a rubber band from knob to front knee"
- Small step forward (stride), controlled, not lunging
- Weight loads into back hip/leg (coil)
- Hands work back, knob toward catcher
- Start early enough: when front foot lands, ready to swing
- **Common flaw:** Falling forward early, no load into back hip

### Launch Position
- Front foot has landed in strong athletic position
- Knob pointed toward catcher
- Hands back in a strong spot
- Balanced and under control, not rushing
- Head still, eyes tracking pitch
- **This is the "ready" position — window to decide swing or take**

### Swing Mechanics (Sequence & Turn)
- Hips initiate first (lower half leads)
- Core engages, creating hip-shoulder separation
- Avoid hands going early before lower body turns
- Maintain posture — don't stand up or lean back
- Staying centered is critical
- **Common flaw:** Upper body leading, spinning out, flying open

### Connection & Bat Path
- Barrel stays tight to body (connected, not casting)
- Short, compact swing — inside the ball
- Back elbow slots into the body (not dragging or flying out)
- Barrel above or even with hands at the turn point
- Level or slightly upward path through the zone
- Palm up/palm down through contact zone
- **Common flaws:** Casting (hands away from body), disconnected/long swing, barrel dropping early, rolling wrists too early

### Contact & Extension
- Contact point relative to front foot: middle pitch slightly out front, outside pitch at front knee, inside pitch further out front
- Palm up (top hand) / palm down (bottom hand) at contact
- Rear elbow connected to body
- Hitting inside part of baseball
- Extend barrel through the ball toward target
- **Common flaws:** Rolling over, cutting across ball, poor contact point for pitch location

### Finish & Balance
- Balanced finish — ability to hold it for 2 seconds ("Stick It Drill")
- Chin finishes on back shoulder (head stayed down)
- Can finish one hand or two
- Not flying open, spinning out, or falling forward/back
- **If balance is off at finish, something went wrong earlier in the swing**

## Key Angles for Analysis

| Metric | What It Measures | What to Look For |
|--------|-----------------|------------------|
| Hip-Shoulder Separation | Sequencing quality | Should build from ~5-10 at launch to 40-55+ at contact. Hips lead. |
| Back Elbow Angle | Connection/slot | Starts high (~30-60 in stance), works toward ~90 at slot, opens through contact |
| Front Knee Angle | Front side firmness | Should firm up (straighten toward 170-180) at/after contact — "blocking" |
| Back Knee Angle | Drive from back leg | Drives forward during swing, collapses at finish |
| Spine Tilt | Posture maintenance | Should stay relatively consistent (5-15 from vertical) — not standing up or leaning excessively |
| Shoulder Line Angle | Shoulder rotation/tilt | Tracks rotation through swing + any shoulder dipping |
| Hip Line Angle | Hip rotation | Tracks how much hips have opened toward pitcher |

## Rotation Analysis

Rotation is measured via the angles of the hip and shoulder lines relative to horizontal.

For a right-handed batter from a side/behind-catcher camera angle:
- **MediaPipe left side = front side** (facing pitcher)
- **MediaPipe right side = back side** (facing catcher)
- Hip-shoulder separation = normalized angular difference between hip line and shoulder line
- Separation should be small at stance, build during load, and peak around contact

The "tornado effect" or "swing sequence from the ground up" means:
1. Feet/ground connection initiates
2. Hips rotate first
3. Separation builds as shoulders lag
4. Shoulders catch up, hands deliver barrel
5. Maximum separation occurs just before or at contact

## Common Issues to Flag

From Assessment Form checklist:
- Drops barrel / Casts hands / Hands disconnect from body
- Pulls off ball / Flying open / Spinning out
- Lunges forward / Falls forward or backward
- No rhythm (static) / Poor timing
- Upper half starts before lower half (out of sequence)
- Steep/chopping bat path or scooping
- Head movement (pulling head up/out)
- Rolling over (early wrist roll)
