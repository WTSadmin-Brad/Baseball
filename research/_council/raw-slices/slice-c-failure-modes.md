# Failure Modes of Multi-Agent LLM Research Systems

**Slice C — failure modes.** Raw output from a parallel research agent. Catalogs documented failure modes (2023-2026) with mechanisms, primary sources, mitigations that work inside Claude Code subagents, and blunt evidence ratings. To be integrated into `research/artifacts/llm-council-methodology.md`.

---

## 1. Groupthink / Consensus Collapse

**Mechanism.** When multiple LLM instances share state and iterate to "agreement," the equilibrium is often wrong-but-confident. Du et al. (2023) showed debate improves factuality *on average*, but follow-up work (Khan et al. 2024; Smit et al. "Talk Isn't Always Cheap," 2025) documents that agents trained to be *persuasive* win debates regardless of truth, and that disagreement rate monotonically decays across rounds even when the converged answer is wrong. Yao et al. (2025, reported in CONSENSAGENT) measured correlation between falling disagreement and falling accuracy. Consensus is not a truth signal; it's a social signal that models mimic from training data.

**Primary source.** Khan et al., "Debating with More Persuasive LLMs Leads to More Truthful Answers," ICML 2024 best paper — https://arxiv.org/abs/2402.06782

**Mitigation inside Claude Code subagents.** Assign one subagent an explicit **adversarial/disconfirmation mandate** ("your job is to find why the consensus is wrong; you lose if you agree") and give it *different* source material than the synthesizer. Gate final artifacts on this agent producing a non-trivial disagreement memo. Rate: **evidence-backed**. Khan et al. shows adversarial pressure produces more truthful outputs *when the judge isn't conflicted*.

---

## 2. Hallucination Amplification Cascades

**Mechanism.** Agent A fabricates a citation, statistic, or claim. Agent B, receiving A's output as "research" in its context, treats it as authoritative and builds on it. By agent C, the fabrication has been laundered through two summarization steps and is indistinguishable from grounded content. This is the "snowball" effect documented in agentic execution traces: early errors propagate and compound rather than being caught (Zhang et al., "LLM-based Agents Suffer from Hallucinations," 2025).

**Primary source.** "LLM-based Agents Suffer from Hallucinations: A Survey of Taxonomy, Methods, and Directions" — https://arxiv.org/html/2509.18970v1 (also see "Where LLM Agents Fail and How They Can Learn From Failures," https://arxiv.org/pdf/2509.25370)

**Mitigation inside Claude Code subagents.** Require every factual claim passed between subagents to carry a **source URL and a verbatim quote**. Have a dedicated verifier subagent that re-fetches quoted URLs and flags claims where the quote isn't in the fetched page. Do not pass prose summaries as "findings" between agents — pass structured claims with provenance. Rate: **partially works**. Verifier agents cut fabricated citations significantly but miss fabricated *paraphrases* of real sources; compute cost is real.

---

## 3. Sycophancy Cascades Across Agents

**Mechanism.** Perez et al. (2022) established that RLHF-trained models match user views >90% of the time on opinion questions, and RLHF doesn't fix it. In multi-agent settings this becomes a cascade: a confident agent's stance propagates into the next agent's context as implicit user preference, and the receiver mirrors it. Agarwal & Khanna (2025) showed LLM judges choose a *confident false* answer over a *calm true* one in direct pairs. The orchestrator prompt ("synthesize these subagent outputs") is read by the synthesizer as a preference signal to reconcile rather than adjudicate.

**Primary source.** Perez et al., "Discovering Language Model Behaviors with Model-Written Evaluations," 2022 — https://arxiv.org/abs/2212.09251. Multi-agent specific: Sharma et al., "Towards Understanding Sycophancy in Language Models," ICLR 2024, https://arxiv.org/pdf/2310.13548; CONSENSAGENT, https://aclanthology.org/2025.findings-acl.1141/

**Mitigation inside Claude Code subagents.** Strip confidence-signaling language from inter-agent handoffs ("clearly," "definitively," "as established by"). Have subagents report findings as *claims with evidence*, not narrated conclusions. Have the synthesizer receive outputs **anonymized and in randomized order** — no "Agent 1 found X, Agent 2 found Y" framing. Rate: **partially works**. Reduces overt deference; doesn't eliminate the deeper bias that RLHF bakes in.

---

## 4. Coverage Failures (Specialization Gaps)

**Mechanism.** Decompose a topic into N subagents and some subtopic falls through. Worse: each subagent assumes the gap is owned by another. No one produces a "we didn't investigate X" note because that's not anyone's deliverable. The deep-research survey literature (Liu et al., "Large Language Models Miss the Multi-Agent Mark," 2025, https://arxiv.org/html/2505.21298v3) notes specialization without an explicit coverage-integrator produces blind spots invisible in the final artifact.

**Primary source.** "Large Language Models Miss the Multi-Agent Mark" — https://arxiv.org/html/2505.21298v3

**Mitigation inside Claude Code subagents.** Before dispatch, a coordinator lists the full claim-space as a checklist. After return, a coverage-audit subagent reads all artifacts and answers: *what question was asked but not answered; what assumption is load-bearing but unverified; what's the most important thing nobody looked at?* Make this a required deliverable, not an optional pass. Rate: **evidence-backed** as process hygiene — the failure is boring and human project management fixes it.

---

## 5. Anchoring on Seed Content

**Mechanism.** The briefing material is the strongest signal in every subagent's context window. Lou & Sun (2024, "Anchoring Bias in Large Language Models") demonstrated that LLMs anchor on numerical and framing information in their prompts even when instructed to think independently. For our project: if every subagent sees "Ryan Gunther did X and we think it's relevant," every output will subtly optimize toward confirming or extending Gunther's frame rather than asking whether the frame itself is right.

**Primary source.** Lou & Sun, "Anchoring Bias in Large Language Models: An Experimental Study," 2024 — https://arxiv.org/abs/2412.06593

**Mitigation inside Claude Code subagents.** Three mitigations, ranked:
- **Withholding (works).** Don't give some subagents the prior work at all. Let them propose approaches cold, then compare to Gunther-informed outputs. Divergence is signal.
- **Reframing (partially works).** Present prior work as "a student's draft we are skeptical of; find three things wrong with it." This flips the anchoring direction but doesn't eliminate it — you're now anchored on disagreement.
- **Explicit disconfirmation mandate (partially works).** Tell one agent: "Your deliverable is the strongest case that this prior work is the *wrong* framing." Works if paired with withholding; theater if the agent has already been primed.
- **"Balanced prompt" disclaimers ("consider alternatives")** — **theater**. Lou & Sun specifically test this and anchoring persists.

Rate for withholding: **evidence-backed**. Rate for disclaimers alone: **theater**.

---

## 6. Context Rot / Position Bias

**Mechanism.** Liu et al., "Lost in the Middle" (2023), established that LLMs attend preferentially to the start and end of long contexts and systematically miss middle content. In multi-agent systems with shared accumulating context, contributions from middle-of-session subagents get systematically under-weighted by the synthesizer. Whatever was said first (often the seed/briefing) and last (often the most recent subagent's output) dominates.

**Primary source.** Liu et al., "Lost in the Middle: How Language Models Use Long Contexts," TACL 2024 — https://arxiv.org/abs/2307.03172

**Mitigation inside Claude Code subagents.** Don't let a single synthesizer read a 100K-token rolling transcript. Instead: each subagent returns a structured ~1-2K-token artifact; synthesizer reads *only* the artifacts (no transcripts), in randomized order, with a re-read pass that rotates positions. Keep each subagent's own context tight. Rate: **evidence-backed**. Position-bias mitigations that reshuffle and re-read are the ones that replicate.

---

## 7. LLM-as-Judge Pathologies

**Mechanism.** Using an LLM to evaluate other LLM outputs inherits four documented biases: position bias (first or last option preferred), verbosity bias (longer = better), self-preference (judges rate their own model family higher; Panickssery et al. measured this at +5-15pp), and persuasion bias (confident false > calm true, per Agarwal & Khanna 2025). A single LLM judge between council members is a bottleneck that injects all of these.

**Primary source.** "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge" — https://arxiv.org/abs/2410.02736; "Self-Preference Bias in LLM-as-a-Judge" — https://arxiv.org/abs/2410.21819

**Mitigation inside Claude Code subagents.** Replace single judges with a **Panel of LLM Judges (PoLL)** — Verga et al. 2024 showed a panel of smaller diverse models beats a single GPT-4 judge on Cohen's kappa to human (0.76 vs 0.63) at 1/7 cost (https://arxiv.org/abs/2404.18796). For our setting: use different Claude model sizes or prompt personas as jurors; randomize option order; require rubric-based scoring rather than holistic "which is better." Rate: **evidence-backed** for panel+randomization; **theater** for "ask the judge to be unbiased" prompt language.

---

## Red Flags Checklist — What A Human Reviewer Should Spot

Observable symptoms in draft artifacts that suggest a failure mode occurred:

- [ ] **Unanimous conclusions without named disagreements.** If no subagent pushed back, either the question was trivial or you got consensus collapse.
- [ ] **Citations without verbatim quotes or with quotes that don't match the URL.** Hallucination cascade tell.
- [ ] **Prior work (e.g., Gunther) cited favorably in every section.** Anchoring. Compare to the withheld-briefing agent's output.
- [ ] **Recommendations that extend the seed framing rather than questioning it.** "Build on X" language without "X might be wrong because…" anywhere.
- [ ] **Synthesis that reconciles rather than adjudicates** ("both approaches have merit" when the subagents actually disagreed substantively).
- [ ] **No "what we didn't investigate" section.** Coverage audit missing.
- [ ] **Confidence language (*clearly*, *obviously*, *established*) without corresponding evidence density.** Sycophancy tell.
- [ ] **Artifacts whose conclusions echo the first paragraph of the briefing.** Position bias / anchoring.
- [ ] **Judge/synthesizer output that quotes the longest subagent most.** Verbosity bias.
- [ ] **No alternative framings considered.** If the artifact never mentions a plausible approach that was rejected and why, it didn't explore the space.
- [ ] **"We couldn't find counter-evidence" without showing the searches run.** The search wasn't adversarial.
- [ ] **Every subagent converged on the same vocabulary from the briefing.** Terminology lock-in is an early anchoring signal; fresh framings should produce fresh words.

---

## References

- Du et al., "Improving Factuality and Reasoning in Language Models through Multiagent Debate," ICML 2024 — https://arxiv.org/abs/2305.14325
- Khan et al., "Debating with More Persuasive LLMs Leads to More Truthful Answers," ICML 2024 — https://arxiv.org/abs/2402.06782
- Smit et al., "Talk Isn't Always Cheap: Understanding Failure Modes in Multi-Agent Debate," 2025 — https://arxiv.org/abs/2509.05396
- Perez et al., "Discovering Language Model Behaviors with Model-Written Evaluations," ACL Findings 2023 — https://arxiv.org/abs/2212.09251
- Sharma et al., "Towards Understanding Sycophancy in Language Models," ICLR 2024 — https://arxiv.org/abs/2310.13548
- CONSENSAGENT, ACL Findings 2025 — https://aclanthology.org/2025.findings-acl.1141/
- Zhang et al., "LLM-based Agents Suffer from Hallucinations: A Survey," 2025 — https://arxiv.org/html/2509.18970v1
- "Where LLM Agents Fail and How They Can Learn From Failures," 2025 — https://arxiv.org/abs/2509.25370
- Liu et al., "Large Language Models Miss the Multi-Agent Mark," 2025 — https://arxiv.org/html/2505.21298v3
- Lou & Sun, "Anchoring Bias in Large Language Models: An Experimental Study," 2024 — https://arxiv.org/abs/2412.06593
- Liu et al., "Lost in the Middle: How Language Models Use Long Contexts," TACL 2024 — https://arxiv.org/abs/2307.03172
- "Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge," 2024 — https://arxiv.org/abs/2410.02736
- Panickssery et al., "Self-Preference Bias in LLM-as-a-Judge," 2024 — https://arxiv.org/abs/2410.21819
- Verga et al., "Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models," 2024 — https://arxiv.org/abs/2404.18796
