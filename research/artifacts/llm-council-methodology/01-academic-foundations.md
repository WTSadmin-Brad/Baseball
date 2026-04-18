# Multi-Agent LLM Systems for Deep Research: Academic Literature 2022-2026

**Slice A — academic foundations.** Raw output from a parallel research agent. Covers patterns/architectures, whether role specialization actually helps, adversarial/critic roles, consensus mechanisms, and 2024-2026 developments. To be integrated into `research/artifacts/llm-council-methodology.md`.

---

## 1. Patterns and architectures

- **Multi-agent debate (MAD) — reasoning convergence.** Du et al. (2023) have N identical agents propose answers, read peers' rationales, and iterate to a shared answer; gains on math/factuality [Du 2023]. Liang et al. (2023) inject an explicit *judge* plus two *divergent* debaters to counter "degeneration of thought" in homogeneous debate [Liang 2023].
- **Role-playing societies.** CAMEL pairs an *AI-user* and *AI-assistant* via inception prompting to self-generate task-solving dialogues [Li 2023]. NLSOMs (Schmidhuber et al.) scale this to ~100-agent "mindstorms" across modalities [Zhuge 2023].
- **Supervisor–worker / staged pipelines.** MetaGPT encodes an SDLC (PM → architect → engineer → QA) with standardized message artifacts — a classic hierarchical pattern [Hong 2023].
- **Judge / jury frameworks.** ChatEval runs a debate *panel* for open-ended text evaluation; diverse roles outperform single-judge LLM scoring [Chan 2023]. ReConcile is a round-table of *heterogeneous* models (GPT-4, Claude, Bard) using confidence-weighted voting [Chen 2023].
- **Communication-structure variants.** Exchange-of-Thought (EoT) varies topologies — memory, report, relay, debate — as a design axis [Yin 2023]. Li et al. (2024) show *sparse* topologies match dense-debate quality at lower cost [Li 2024].
- **Adversarial probes.** MAgIC benchmarks agents in mixed cooperative/competitive games (Undercover, Chameleon) as a probe of rationality and deception [Xu 2023]. LM-vs-LM Cross-Examination uses an examiner LM to surface factual inconsistencies [Cohen 2023].

## 2. Does role specialization beat same-prompt ensembles on open-ended tasks?

Evidence is mixed and weaker than the hype suggests.

- **Against strong role claims:** Wang et al. ("Rethinking the Bounds") find that on reasoning benchmarks, *a well-prompted single agent matches the best multi-agent discussion* — multi-agent only wins when the single agent lacks demonstrations [Wang 2024]. Li et al.'s "More Agents Is All You Need" shows plain sample-and-vote scales nearly as well as elaborate role scaffolds — i.e., diversity from sampling ≈ diversity from personas [Li 2024b].
- **For role specialization:** ReConcile's ablations show *heterogeneous models* (not just heterogeneous prompts) drive most of the gain — an 8% MATH lift vs. homogeneous debate [Chen 2023]. ChatEval reports that "diverse-role" prompting beats "same-role" panels on open-ended NLG evaluation by a small but consistent margin (~3-5 pts correlation with human judgment) [Chan 2023].

**Bottom line for *research-style* open-ended work:** role specialization helps when it surfaces genuinely different retrieval/framing (e.g., skeptic vs. synthesizer, or different base models). Personas over a single frontier model mostly re-parameterize sampling temperature. The cleanest gains come from **model diversity**, not prompt costumes.

## 3. Adversarial / critic roles and truthfulness

Consistent, replicable deltas — this is where multi-agent earns its compute.

- **Cross-examination (LM-vs-LM):** an adversarial examiner improves factual-error detection on LAMA/TriviaQA by 20-30 F1 points over single-model self-check [Cohen 2023].
- **Debate with a judge** (Liang 2023): adversarial setup produces measurable "divergent thinking" gains (~3-7% on Common MT and Counter-Intuitive QA) vs. collaborative multi-agent, which tends to collapse to early consensus.
- **Du et al. (2023)** specifically attribute hallucination reduction (factuality improves ~5-10 points on biographies task) to agents flagging each other's unsupported claims rather than to raw ensembling.

Caveat: Khan et al. (2024) and follow-ups show debate only improves *judge* accuracy when the judge is weaker than debaters *and* debaters are incentivized to be truthful — naively pitting two helpful assistants rarely produces real adversariality. A devil's-advocate role must be *prompt-enforced to disagree* and ideally grounded in retrieved counter-evidence, or it collapses to sycophancy.

## 4. Consensus mechanisms — which wins for research tasks?

| Mechanism | Works well when | Failure mode |
|---|---|---|
| Majority vote / self-consistency | Closed-form answers | Fails on free-form [Chen 2023b] |
| Universal Self-Consistency (LLM picks most-consistent of N) | Open-ended QA, summarization | Picks most *common* framing, not most *correct* [Chen 2023b] |
| Judge-based (one LLM scores) | Cheap scaling | Known bias — position, verbosity, self-preference; JudgeBench shows GPT-4o barely beats random on hard pairs [Tan 2024] |
| Debate-to-consensus | Reasoning with verifiable answers | On open-ended tasks, tends to *converge prematurely* — thought degeneration [Liang 2023] |
| Confidence-weighted voting (ReConcile) | Heterogeneous model pools | Requires calibrated confidences — often absent |
| Separate synthesizer over preserved disagreements | Research, survey-writing, analysis | Higher cost; depends on synthesizer quality |

**For research-style tasks (the use case here), preserving disagreement and routing to a dedicated synthesizer is the most defensible choice.** Collapsing to a single answer destroys exactly the information that makes multi-agent worth the cost — the minority report that flags an uncertain claim. ChatEval's own ablations suggest multi-turn debate + explicit disagreement logging beats majority voting on open-ended evaluation. Universal Self-Consistency [Chen 2023b] is the best single-shot baseline to beat.

## 5. What's genuinely new in 2024-2026

1. **Topology as a first-class design variable.** Sparse-communication debate matches dense debate at ~40% cost [Li 2024]. Graph-structured interactions are now distillable back into single models (MAGDi, [Chen 2024]), suggesting multi-agent is partly a *training signal generator*, not only an inference-time method.
2. **Skepticism of multi-agent gains on reasoning.** Wang et al.'s "Rethinking the Bounds" [Wang 2024] and "More Agents Is All You Need" [Li 2024b] reframe much of the 2023 debate literature as "sampling diversity in disguise." This is a serious hit to society-of-mind claims on MMLU/GSM8K-style tasks — but does not directly refute multi-agent value on *research* tasks, which no one has benchmarked cleanly.
3. **Judge-reliability crisis.** JudgeBench [Tan 2024] shows LLM judges fail on hard pairs. This undermines any pipeline whose consensus mechanism is "ask a big model." For research output, human-in-the-loop or tool-grounded verification is back on the critical path.
4. **Heterogeneous-model stacks.** ReConcile-style pools (mixing GPT-4, Claude, Gemini, open models) consistently outperform homogeneous pools. In 2024-2026 this has become the default in production deep-research systems.
5. **Cross-examination as a primitive.** Adversarial verification is increasingly treated as a distinct stage (generate → cross-examine → synthesize) rather than embedded in debate — cleaner, cheaper, more auditable.

---

## Recommended patterns (for a deep-research system)

1. **Heterogeneous-model parallel generation + separate synthesizer, with preserved disagreement.** **Strong** evidence. Combines ReConcile's diversity finding [Chen 2023] with research-task needs; avoids judge-reliability pitfalls [Tan 2024]. Default choice.
2. **Adversarial cross-examination stage before synthesis.** **Strong** evidence for factuality gains [Cohen 2023; Du 2023]. Cheap and auditable. Use a *different* model family as examiner.
3. **Sparse debate topology if using debate at all.** **Moderate** evidence [Li 2024]. Don't do fully-connected N-agent debate — waste of tokens.
4. **Supervisor–worker pipelines (MetaGPT-style) for *structured* research deliverables.** **Moderate** evidence — works in SWE but unproven on open-ended analysis. Use when the output has a known schema (e.g., "competitive landscape doc with sections X,Y,Z").
5. **Role-persona ensembles over a single frontier model.** **Speculative.** Wang 2024 and Li 2024b suggest these mostly replicate temperature-sampling diversity. Prefer real model diversity over costumed personas.

---

## References

- [Du 2023] Du et al., "Improving Factuality and Reasoning in Language Models through Multiagent Debate." https://arxiv.org/abs/2305.14325
- [Liang 2023] Liang et al., "Encouraging Divergent Thinking in LLMs through Multi-Agent Debate." https://arxiv.org/abs/2305.19118
- [Li 2023] Li et al., "CAMEL: Communicative Agents for Mind Exploration." https://arxiv.org/abs/2303.17760
- [Zhuge 2023] Zhuge et al., "Mindstorms in Natural Language-Based Societies of Mind." https://arxiv.org/abs/2305.17066
- [Hong 2023] Hong et al., "MetaGPT: Meta Programming for Multi-Agent Collaborative Framework." https://arxiv.org/abs/2308.00352
- [Chan 2023] Chan et al., "ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate." https://arxiv.org/abs/2308.07201
- [Chen 2023] Chen et al., "ReConcile: Round-Table Conference Improves Reasoning via Consensus among Diverse LLMs." https://arxiv.org/abs/2309.13007
- [Chen 2023b] Chen et al., "Universal Self-Consistency for Large Language Model Generation." https://arxiv.org/abs/2311.17311
- [Yin 2023] Yin et al., "Exchange-of-Thought: Enhancing LLM Capabilities through Cross-Model Communication." https://arxiv.org/abs/2312.01823
- [Xu 2023] Xu et al., "MAgIC: Investigation of LLM-Powered Multi-Agent in Cognition, Adaptability, Rationality and Collaboration." https://arxiv.org/abs/2311.08562
- [Cohen 2023] Cohen et al., "LM vs LM: Detecting Factual Errors via Cross Examination." https://arxiv.org/abs/2305.13281
- [Wang 2024] Wang et al., "Rethinking the Bounds of LLM Reasoning: Are Multi-Agent Discussions the Key?" https://arxiv.org/abs/2402.18272
- [Li 2024] Li et al., "Improving Multi-Agent Debate with Sparse Communication Topology." https://arxiv.org/abs/2406.11776
- [Li 2024b] Li et al., "More Agents Is All You Need." https://arxiv.org/abs/2402.05120
- [Chen 2024] Chen et al., "MAGDi: Structured Distillation of Multi-Agent Interaction Graphs." https://arxiv.org/abs/2402.01620
- [Tan 2024] Tan et al., "JudgeBench: A Benchmark for Evaluating LLM-based Judges." https://arxiv.org/abs/2410.12784
