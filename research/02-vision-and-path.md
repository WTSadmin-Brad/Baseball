# Vision & Path Preferences

> Last updated: 2026-04-09

---

## Personal Context

The person building this is a **youth travel ball coach** with a **step-son who has generational natural talent**. Baseball is a massive part of their lives and will continue to be for years. The step-son's development — potentially all the way through high school, college, and beyond — is a long-term journey that this tool is meant to support.

This isn't a weekend project or a resume builder. It comes from a genuine obsession with mechanics and analysis, a desire to apply technical skills to the sport they love, and a belief that **MLB-level feedback and analysis should be accessible to every serious player and coach**, not just those with access to $50K motion capture labs.

A previous attempt at this project (~1 year ago) generated incredible feature ideas but never moved forward to implementation. This time the approach is different: methodical, research-driven, and grounded in what's actually technically possible today.

---

## The Path Question

The honest answer: **it's too early to decide.** And that's the right answer.

### Option A — Personal Tool
Build it for:
- The step-son's multi-year development tracking
- The youth travel ball team
- Personal coaching workflow improvement

**Advantages:** No compromises for other users, faster iteration, can be opinionated about workflow, no monetization pressure, can use expensive cloud APIs freely for a small user base.

**Looks like:** Desktop/local app, maybe a simple web deployment, tight integration with the specific coaching methodology and assessment framework from the research PDFs.

### Option B — Product
Build something every baseball fan would love to use.

**Advantages:** Larger impact, potential revenue, community feedback drives improvement, motivation from users, potential partnerships (Driveline, equipment companies, training facilities).

**Looks like:** Mobile-first, cloud-native, multi-tenant, subscription model, onboarding flows, customer support, marketing, app store presence.

### The Decision Framework
> Build the best possible tool for personal use. If it's genuinely great, the product question answers itself.

This means:
1. **Don't cut corners** on analysis quality — build it as if it's a product
2. **Don't over-engineer** infrastructure — keep it simple enough to iterate fast
3. **Do invest heavily** in the AI/ML pipeline — this is the differentiator
4. **Do track the step-son's progression** as the primary use case and validation
5. **Let quality attract opportunity** — if coaches see it and want it, that's the signal

---

## Core Philosophy

### 1. Analysis Must Lead to Action
Numbers without context are useless. "Your hip-shoulder separation is 32 degrees" means nothing to a 12-year-old or their parent. The tool must translate metrics into:
- What's good about this swing
- What needs work
- Specific drills to address it
- Age-appropriate language

### 2. Track Development Over Time
A single swing analysis is a snapshot. The real value is in **longitudinal tracking**: How has this player's mechanics evolved over weeks, months, seasons? Are they regressing? Improving? Plateauing? This is what no consumer app does well.

### 3. Ground-Up Biomechanical Accuracy
Use the best available science. Don't guess at what "good" looks like — use data from Driveline's OpenBiomechanics dataset, published research, and validated biomechanical models. If MLB teams use it, we should understand it.

### 4. Coach-First, Not Data-First
The UI should feel like a coaching tool, not a data dashboard. Think: "What would a great hitting instructor want to see and share with a player's family?" Not: "How many charts can we fit on screen?"

### 5. Camera-Only, No Hardware Required
The magic is in making a phone camera sufficient. No bat sensors, no wearables, no markers. If a parent can film cage work on their iPhone, that's all the input the system should need.

---

## What Success Looks Like

### Minimum (Personal Tool)
- Upload a video of the step-son's swing, get comprehensive AI-powered analysis with coaching cues
- Track his development across a full season with trend analysis
- Compare his mechanics across time periods
- Generate shareable reports for coaches or instructors
- Have the team's swings in one place for the coaching staff

### Stretch (Power Tool)
- Bat tracking from phone video (even approximate)
- Pitch-context-aware analysis (inside vs. outside, up vs. down)
- AI practice planner based on detected weaknesses
- Side-by-side comparison with pro swing archetypes
- Real-time or near-real-time analysis at the cage

### Dream (Product)
- The app that every travel ball parent downloads
- Used by private instructors as their primary analysis tool
- Integrated with league/tournament systems
- Community features (shareable analysis, coaching marketplace)
- Partnership with equipment companies or training facilities

---

## Non-Negotiables

1. **Accuracy over speed** — Wrong analysis is worse than no analysis
2. **Privacy** — Player data (especially minors) is sacred. No selling data. No social features that expose kids without parental consent.
3. **Offline capability** — Cages and fields don't always have WiFi
4. **Cost-accessible** — If this becomes a product, it must be affordable for the average travel ball family (already spending $3-5K/year on the sport)
5. **Honest about limitations** — The app should be transparent about confidence levels. "I'm not sure about this detection" is better than a wrong answer presented with false confidence.
