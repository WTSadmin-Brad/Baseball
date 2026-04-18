# Part V — Subagents vs Agent Teams: an open design question

**Status:** resolved in favor of subagents for Phase 2; agent teams flagged as a possible Phase 3 extension. Short honest answer to the question raised during Phase 1 planning: "are we locking into subagents when agent teams might be better?"

---

## The tradeoff

| | **Claude Code subagents** (Agent tool) | **Claude Code agent teams** (experimental) |
|---|---|---|
| API | Stable, GA | Experimental, requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, v2.1.32+ |
| Unit | A fresh context window spawned from a parent session | A separate Claude Code *session* with its own transcript |
| Peer dialogue | None. Each invocation returns one text response to parent. | Sessions can message each other during a run. |
| Nesting | Subagents cannot spawn subagents. One level of delegation. | Teams can form hierarchies. |
| State | No shared memory by default; disk is the only bulletin board. | Same, plus live inter-session messaging. |
| Failure surface | Small. If a subagent fails, the parent retries. | Larger. Cross-session coordination can deadlock or drift. |
| Today's use case coverage | Orchestrator-worker, parallel fan-out, sequential pipelines, critic pass. | Adds: live debate, negotiation, joint artifact construction. |

Docs: [subagents](https://code.claude.com/docs/en/sub-agents), [agent teams](https://code.claude.com/docs/en/agent-teams).

---

## The evidence that resolves it

Two findings from Parts I–III bear directly on this choice:

1. **Slice A's role-specialization skepticism.** Wang et al. 2024 ("Rethinking the Bounds") and Li et al. 2024 ("More Agents Is All You Need") argue that most gains from multi-agent *discussion* on a single frontier model replicate sampling diversity. The cleanest multi-agent wins come from (a) genuine model diversity (ReConcile-style heterogeneous stacks) and (b) adversarial cross-examination. Live peer dialogue between same-model agents is not where the evidence points.

2. **Slice C's anchoring mitigation hierarchy.** The most effective mitigation for seed-content anchoring is *withholding* — give some agents the prior work, some not, then compare. That works equally well as post-hoc artifact comparison (subagents + synthesizer) or as live debate (agent teams). Post-hoc is simpler, cheaper, and auditable.

The case for agent teams in a research council therefore reduces to: *is there a research question whose answer requires live peer dialogue between agents that cannot be faithfully reconstructed from independent artifacts plus a synthesizer?* We have not identified one for Phase 2.

---

## Recommendation

**Proceed with subagents for Phase 2.** Filesystem handoff is sufficient for the research workload we're planning (diverse framings + synthesis + optional critic pass). The Agent tool is already the supervisor pattern Anthropic's own research system uses.

**Flag agent teams as a Phase 3 extension if:**

- Phase 2 artifacts show insufficient disagreement surfacing — i.e., the synthesizer produces "both approaches have merit" conclusions where subagents actually disagreed, and post-hoc comparison isn't forcing the disagreements into the open.
- A future research question genuinely demands live debate (e.g., structured red-team-vs-blue-team cross-examination where each side's responses are conditioned on the other's rebuttals in real time).
- The experimental API matures enough that coordination overhead stops being a net loss.

**Do not block Phase 2 on this.** The cost of being wrong is low: the research artifacts produced by subagents are the same *content* you'd get from agent teams, just assembled at the end rather than in-flight. If the synthesis quality is insufficient, we can replay individual slices or add a debate pass later without throwing away work.
