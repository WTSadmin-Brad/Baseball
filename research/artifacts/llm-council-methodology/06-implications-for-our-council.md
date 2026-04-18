# Part VI — Implications for the baseball swing analysis research council

**This part connects Phase 1 methodology findings to the Phase 2 deliverable** — designing the specific council that will research baseball swing analysis from monocular phone video. It surfaces the design calls that fall out of the evidence in Parts I–IV. It does not yet design the council; that's Phase 2.

---

## 1. The model-diversity dilemma

Slice A's strongest finding: the cleanest multi-agent wins come from **heterogeneous models**, not heterogeneous personas on a single model. Wang 2024 and Li 2024b show role-persona ensembles mostly replicate sampling diversity. ReConcile [Chen 2023] gets real gains from actually different base models (GPT-4 + Claude + Gemini).

We are committing to all-Claude subagents (per the user's implementation choice). We cannot use model heterogeneity as our diversity source. So we must substitute. The evidence supports four substitutes, in roughly this order of effectiveness:

1. **Information asymmetry.** Some agents get the Gunther thesis findings in their brief; others work from a cold search. Slice C's top anchoring mitigation. Divergence between informed and uninformed artifacts is itself signal.
2. **Tool and source asymmetry.** Different agents get different WebSearch scopes (arXiv-only vs broad web vs sports-specific), different read access to the repo, different allowed domains. Forces different information ingest.
3. **Adversarial mandate asymmetry.** At least one agent has a disconfirmation mandate: "your deliverable is the strongest case that our current approach is wrong." Works only when paired with information asymmetry — a disconfirmer who has already read the seed will anchor anyway (Lou & Sun 2024).
4. **Model-tier asymmetry.** Route exploration-only slices to Haiku 4.5; route synthesis and critic passes to Opus 4.7 or Sonnet 4.6. Not real diversity but non-trivial behavioral variation and useful cost control.

## 2. Gunther-anchoring is the top concern; handle it surgically

The user explicitly flagged anchoring on Ryan Gunther's prior work as the dominant risk. Slice C's evidence hierarchy:

- **Withholding** (evidence-backed) — at least one council member does not see the Gunther findings at all.
- **Reframing as flawed draft** (partially works) — only valuable if paired with withholding; solo it just flips the anchor direction.
- **Explicit disconfirmation mandate** (partially works) — the red-team role.
- **"Balanced prompt" disclaimers** (theater) — do not rely on these.

Phase 2 concrete implication: among the ~6-10 council members, at minimum **two must be withheld**: a cold-search pose-estimation researcher and a cold-search bat-tracking researcher. Their artifacts become the check against seed-anchored conclusions.

## 3. Adversarial cross-examination as a distinct role

Slice A calls cross-examination one of the strongest-evidence multi-agent patterns (Cohen 2023: +20-30 F1 on factual-error detection). Slice B calls it a standalone stage ("generate → cross-examine → synthesize") rather than a prompt flavor embedded in debate.

Phase 2 concrete implication: the council has a dedicated **Cross-Examiner** member whose input is other members' artifacts and whose output is a verification memo — claims with unverifiable citations, claims where the cited URL doesn't support the claim, claims that contradict peer artifacts. This is not the same role as the red-team/disconfirmer; they run in parallel.

## 4. Preserve disagreement; do not collapse to consensus

Slice A's consensus table: majority vote and judge-based aggregation are weak on open-ended research tasks; the strongest pattern is "preserved disagreement routed to a dedicated synthesizer." Slice C reinforces: if the final artifact has no named disagreements, that's a red flag, not a success.

Phase 2 concrete implication: the synthesis step produces a **decision memo with explicit minority reports**, not a reconciliation. Where the withheld-brief cold-search slice contradicts the informed slice, both views are named and the reasoning for preferring one (or keeping both open) is given.

## 5. Panel of judges, not single judge

Slice C: single LLM judges carry position, verbosity, self-preference, and persuasion biases. Verga et al. 2024 show panel-of-judges beats single-GPT-4 at 1/7 cost on kappa-to-human.

Phase 2 concrete implication: quality gates (e.g., "does this artifact meet the senior-engineer-decision bar?") use a panel — different Claude model tiers or different rubric personas — with randomized option order. Not a single "judge" agent.

## 6. Two human checkpoints

Slice B: the two predictable HITL points that save the most wasted spend are (a) post-plan, pre-dispatch and (b) pre-synthesis artifact review.

Phase 2 concrete implication: the orchestrator does not fan out until the user has seen and approved the plan. After fan-out, artifacts are surfaced before synthesis so the user can kill or retry weak ones. Both are cheap; both prevent the most common failure modes.

## 7. Token budget and pragmatics

Slice D: budget ~500k tokens for a full 8-slice pass on Sonnet 4.6. Anthropic reports ~15× chat token cost on their own research system. This is the cost of being right.

Phase 2 concrete implication: the council is not cheap. It is not a loop you run a dozen times to polish wording. It is a single concerted research pass per major topic, with replay of individual slices where results are weak. Plan topics and sequencing accordingly; do not run the full council on trivial questions.

## 8. What Phase 2 will produce

Phase 2 will turn the above implications into concrete subagent definition files under `.claude/agents/council-*.md`, a shared brief at `research/_council/brief.md`, an orchestrator protocol document, and a first-pass research mandate list covering the "What I Believe Is Missing" gaps from the project prompt (2024-2026 pose estimation SOTA, cross-discipline transfer, biomechanical engines, datasets, training strategies, IMU extraction feasibility, bat/ball tracking, novel pipeline architectures). Each council member will have: a role and non-overlapping mandate; an information-asymmetry assignment (informed vs withheld); a tool allowlist; a model tier; and an output artifact template.

Phase 1 is done. Phase 2 design is the next deliverable.
