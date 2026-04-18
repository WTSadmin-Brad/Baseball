# LLM Council Methodology for Deep Research

**Phase 1 deliverable.** Methodology for designing an LLM council of Claude Code subagents to conduct deep research. Synthesizes academic literature (2022-2026), production patterns from shipping systems, documented failure modes, and Claude Code-specific orchestration mechanics. Phase 2 — the specific baseball swing analysis research council — will be designed using these findings as input.

**Structure.** This artifact is multi-file by design (the single-file synthesis write kept timing out at 5–6k words). Each Part is independently readable; the executive summary below is the one-stop read for decisions.

| Part | File | Topic |
|---|---|---|
| I | [01-academic-foundations.md](01-academic-foundations.md) | Patterns, specialization evidence, critic roles, consensus, 2024-2026 developments |
| II | [02-practitioner-reality.md](02-practitioner-reality.md) | Anthropic's orchestrator-worker, Cognition's counter, frameworks, HITL |
| III | [03-failure-modes.md](03-failure-modes.md) | Seven documented failure modes, mitigations, red-flags checklist |
| IV | [04-orchestration-plumbing.md](04-orchestration-plumbing.md) | Brief, handoff template, disk as state, token budget, subagent format, topology |
| V | [05-subagents-vs-agent-teams.md](05-subagents-vs-agent-teams.md) | The open design question, resolved |
| VI | [06-implications-for-our-council.md](06-implications-for-our-council.md) | What falls out for the baseball swing analysis council |

---

## Executive summary — the decisions that fall out

**1. Role-persona ensembles over a single frontier model mostly replicate sampling diversity** [Wang 2024; Li 2024b]. Since we're committing to all-Claude subagents, we cannot get ReConcile-style model heterogeneity. We must substitute. The four substitutes, in order of evidenced effectiveness: **information asymmetry** (withheld vs informed seed material), **tool/source asymmetry**, **adversarial mandate asymmetry**, model-tier asymmetry.

**2. Withholding seed material from at least some council members is the top-evidence anchoring mitigation** [Lou & Sun 2024]. "Balanced prompt" disclaimers ("consider alternatives") are theater. For the baseball council this means at least two members must be cold-search (no exposure to the Gunther thesis or our prior synthesis) whose artifacts become the check on seed-anchored conclusions.

**3. Adversarial cross-examination is a distinct stage, not a prompt flavor** [Cohen 2023; Du 2023]. Generate → cross-examine → synthesize. The Cross-Examiner reads other members' artifacts and produces a verification memo: unverifiable citations, URL-quote mismatches, peer-artifact contradictions. This is separate from the disconfirmer / red-team role; they run in parallel.

**4. Preserve disagreement; do not collapse to consensus.** Majority vote and single-judge aggregation are weak on open-ended research [JudgeBench, Tan 2024]. The strongest pattern is preserved-disagreement routed to a dedicated synthesizer. The final decision memo names minority reports explicitly.

**5. Use a panel of judges, not a single judge, for any quality gate** [Verga 2024]. Different Claude model tiers or rubric personas, randomized option order, rubric-based scoring. Single-judge LLM evaluators carry position, verbosity, self-preference, and persuasion biases.

**6. Adopt Anthropic's orchestrator-worker + plan-and-execute pattern** [Anthropic 2025]. Parallel fan-out of 3–5 subagents, conditional re-plan at synthesis. Cognition's "Don't Build Multi-Agents" critique doesn't bind us — our agents emit artifacts, not shared-state mutations. Steal Cognition's lesson anyway: pass full artifacts (not bullet summaries) to the synthesizer.

**7. Two human checkpoints: post-plan, pre-synthesis.** The plan-approval checkpoint prevents the single most common failure — orchestrator misreading the question. The artifact-review checkpoint prevents one weak worker from poisoning synthesis. Both are cheap; both save ~15× token spend downstream.

**8. Disk is the bulletin board; shared brief ≤1.5k tokens.** Claude Code subagents have no peer-to-peer memory. Use the filesystem (`research/_council/brief.md` + `research/artifacts/...`). Keep the shared brief under 1,500 tokens; above 2k it measurably anchors every slice. Put everything slice-specific in the invocation prompt.

**9. Artifact handoff: YAML frontmatter + front-loaded TL;DR + body.** Orchestrator reads only frontmatter + TL;DR during synthesis; drills into body only on conflict or `confidence: low`. Frontmatter must include slice, confidence, key_claims, open_questions, dependencies_satisfied.

**10. Budget ~500k tokens per full 8-slice council pass** [Anthropic 2025, ~15× chat]. This is not a loop you run a dozen times to polish wording. Plan topics and sequencing accordingly; do not run the full council on trivial questions.

**11. Proceed with subagents for Phase 2; flag agent teams as a possible Phase 3 extension.** Evidence does not support live peer dialogue as a win for this workload; filesystem handoff is sufficient and stable. Revisit if Phase 2 artifacts fail to surface disagreement.

**12. Red flags checklist at the end of Part III is a working document.** Use it when reviewing any Phase 2 output. If an artifact triggers two or more red flags, replay the slice that produced it.

---

## What Phase 2 produces

Using this methodology, Phase 2 will deliver:

- Concrete subagent definition files under `.claude/agents/council-*.md`
- A shared brief at `research/_council/brief.md` (≤1.5k tokens)
- An orchestrator protocol document
- A research mandate list covering the gaps identified in the project prompt (2024-2026 pose estimation SOTA, cross-discipline transfer, biomechanical engines, datasets, training strategies, IMU extraction feasibility, bat/ball tracking, novel pipeline architectures)
- Explicit information-asymmetry assignments (which council members are informed, which are withheld)
- The Cross-Examiner and Disconfirmer roles as distinct members
- Panel-of-judges configuration for quality gates
- Two documented human-checkpoint touchpoints

---

## Meta-note on how this artifact was produced

This methodology was produced by **running a small version of the council itself**: four parallel research slices (A academic, B practitioner, C failure modes, D orchestration) running as Claude Code subagents, with results integrated by the orchestrator. Along the way we hit several of the failure modes Part III documents — the single-file synthesis write timed out repeatedly, which is why the artifact is multi-file. This is a useful ground-truth datapoint: **each council slice should produce a self-contained artifact at moderate length; forcing one agent to integrate everything into a single giant write is fragile in practice.** Phase 2 should design around moderate-length independent artifacts + a thin integration layer (which may itself be multi-file), not around a single omniscient synthesizer.
