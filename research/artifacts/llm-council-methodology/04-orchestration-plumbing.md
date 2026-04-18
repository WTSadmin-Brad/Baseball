# LLM Council Methodology: Context, Handoffs, and Orchestration

**Slice D — plumbing only.** This document covers how context flows between a main Claude Code session and 5–10 specialized research subagents: what goes in the shared brief vs the private mandate, how artifacts get handed off, where state lives, realistic token budgets, the Claude Code subagent format specifics, and a recommended topology. Opinionated throughout; where Anthropic and Cognition disagree I pick a side.

---

## 1. Shared brief vs private mandate: keep the shared surface small

A council subagent is a fresh context window. Every token of shared brief is a token you are re-paying 5–10 times *and* anchoring every slice with. Anthropic's own postmortem says vague briefs caused slices to duplicate work and recommends "explicit objectives, expected output format, tool guidance, clear boundaries" ([Anthropic, *How we built our multi-agent research system*](https://www.anthropic.com/engineering/multi-agent-research-system)). Cognition's counterpoint — that dispersed context produces fragile systems — is valid but applies to *implementing* agents that must edit shared code, not to *research* agents returning documents ([Cognition, *Don't Build Multi-Agents*](https://cognition.ai/blog/dont-build-multi-agents)).

**Rule of thumb: the shared brief should be under ~1,500 tokens.** Above ~2k it starts producing measurable anchoring — every slice's conclusion section echoes the same framing language, which is groupthink you specifically convened a council to avoid. Keep shared content to irreducible facts everyone needs to coordinate.

**Shared brief (all agents see, ≤1.5k tokens):**
- One-paragraph project statement (what we're building, for whom)
- Artifact location + filename convention
- Output spec: word count, required sections, tone
- The list of all slices with one-line descriptions (so slices know what *not* to cover)
- Hard rules: cite sources with URLs, no academic theory recap, no production code

**Private mandate (per-agent, 500–1,500 tokens):**
- The specific question this slice answers
- Success criteria ("a senior engineer could make a decision from this")
- Non-goals explicitly naming what adjacent slices cover
- Opinionated framing where this slice is expected to disagree with defaults
- Suggested sources/search terms unique to this slice

Do **not** put the existing `research/01-*.md` through `04-*.md` in the shared brief. Reference them by path and let slices `Read` what they need. Prior research already gets summarized into CLAUDE.md, which every subagent sees via the environment — do not re-paste it.

---

## 2. Artifact handoff format: structured markdown with a machine-readable header

Pure prose artifacts force the orchestrator to re-read everything. Pure JSON loses the nuance that makes a research document useful to humans. The shipping pattern across LangChain, Mastra, and Anthropic's own agent SDK is **structured markdown with a front-loaded summary** ([LangChain structured output](https://docs.langchain.com/oss/python/langchain/structured-output); [Claude Agent SDK structured outputs](https://platform.claude.com/docs/en/agent-sdk/structured-outputs)).

**Required output template for every council artifact:**

```markdown
---
slice: D
title: Context Management and Orchestration Mechanics
word_count: ~1500
confidence: high | medium | low
open_questions:
  - "Does agent_teams beat plain subagents at 10-way fan-out?"
key_claims:
  - "Shared brief > 2k tokens causes groupthink"
  - "Subagents return text only; no shared state without disk"
dependencies_satisfied: []   # slices whose output this one consumed
---

# Title

## TL;DR (≤150 words)
Front-loaded conclusions. The orchestrator reads ONLY this section when
synthesizing, unless the summary flags something that needs drill-down.

## Key recommendations
Bulleted, opinionated, each actionable.

## Body
Full argument with sources inline.

## Sources
- [Title](URL)
```

The frontmatter lets the orchestrator build a synthesis table without re-reading bodies. The TL;DR is the contract: if it's wrong or thin, the artifact fails review. `key_claims` is the pointer list downstream slices use to decide whether to pull the full body. This mirrors the abstract+drill-down pattern from scientific papers and is what [Mastra](https://mastra.ai/docs/agents/structured-output) and LangChain recommend for agent-to-agent handoffs.

---

## 3. Where state lives: disk is the only shared memory in Claude Code

Claude Code subagents have **no shared memory by default**. Each invocation is a fresh context window; the only inputs are (a) the system prompt from the agent definition, (b) the prompt string passed at invocation, and (c) basic env like cwd ([Claude Code subagents docs](https://code.claude.com/docs/en/sub-agents)). Resumed subagents keep their own transcript but still can't see peers.

This leaves three real options:

1. **Filesystem (recommended for a research council).** Orchestrator writes the shared brief to `research/_council/brief.md`. Each slice writes to `research/artifacts/<slice>-<topic>.md`. Downstream slices that need peer output `Read` the file. This is exactly what Anthropic's research system does: "subagents call tools to store their work in external systems, then pass lightweight references back to the coordinator" ([Anthropic multi-agent post](https://www.anthropic.com/engineering/multi-agent-research-system)).

2. **Persistent memory field.** A subagent definition with `memory: project` gets `.claude/agent-memory/<name>/MEMORY.md` injected into its prompt (first 200 lines or 25KB) on every invocation ([subagents docs §memory](https://code.claude.com/docs/en/sub-agents)). Useful for long-running roles (e.g., a "reviewer" that accumulates heuristics across sessions). Overkill for a one-shot research pass.

3. **LangGraph-style store + checkpointer.** If you outgrow Claude Code, LangGraph offers `graph.compile(checkpointer=..., store=...)` for thread-level + cross-thread state with Postgres/Redis backends ([LangGraph Memory docs](https://docs.langchain.com/oss/python/langgraph/add-memory)). For a 5–10 agent research council this is over-engineered; the filesystem is the right primitive.

**Recommendation: disk is the council's bulletin board.** One `research/_council/` directory, append-only.

---

## 4. Token economics: budget 10–15× a single-agent baseline

Anthropic reports their multi-agent research system uses **~15× the tokens of a chat session and ~4× a single agent** ([Anthropic multi-agent post](https://www.anthropic.com/engineering/multi-agent-research-system)). Token usage alone explains 80% of performance variance. For a 5–10 slice council targeting ~1,500 words each with moderate web search:

- **Per slice:** ~15–40k input tokens (system prompt + brief + tool results) + ~3–5k output. Call it ~50k tokens total per slice with search.
- **Council of 8 slices:** ~400k tokens parallelizable across slices.
- **Orchestrator synthesis pass:** reads 8 TL;DRs + frontmatter (~5k tokens) + selectively drills into bodies. Budget 30–60k.
- **Council total:** ~450–500k tokens for a full research pass.

The spend goes to: tool result tokens (WebSearch and WebFetch return big payloads), system prompts repeated per slice, and the synthesis pass. Claude Sonnet 4.6 is the default pick; route exploration-only slices to Haiku 4.5 via `model: haiku` in frontmatter to cut cost ~4× on those slices.

---

## 5. Claude Code subagent specifics

### Definition file format
Subagent files live at `.claude/agents/<name>.md` (project scope) or `~/.claude/agents/<name>.md` (user scope). YAML frontmatter + markdown body. Only `name` and `description` are required ([Claude Code subagents docs](https://code.claude.com/docs/en/sub-agents)).

**All available frontmatter fields:** `name`, `description`, `tools`, `disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`. Defaults: `model: inherit`, tools inherited from parent, no memory.

### Isolation semantics (the important parts)
- Each subagent invocation is a fresh context window. No peer visibility.
- Subagents **cannot spawn other subagents.** One level of delegation only.
- Working directory starts at the parent's cwd; `cd` doesn't persist between bash calls. Set `isolation: worktree` for a throwaway git copy.
- Tool allowlist via `tools: Read, Grep, Glob, WebSearch, WebFetch, Write`. Or `disallowedTools: Write, Edit` to inherit-minus.
- Subagent transcripts persist in `~/.claude/projects/{project}/{session}/subagents/agent-{id}.jsonl` and survive main-thread compaction.

### What you can pass in, what you get back
- **In:** the prompt string the orchestrator writes. That's it. No structured state, no shared memory (unless `memory:` is set, which reads from disk).
- **Out:** a single text response. Anything structured must be parsed by the orchestrator or (better) the subagent writes a file and returns only a file path + TL;DR.

### Council pattern given these constraints
Because you can't pass structured state, the "shared brief + private mandate" pattern becomes:

1. Orchestrator writes `research/_council/brief.md` once at council start.
2. Each slice's agent definition says: *"First `Read` `research/_council/brief.md` in full. Then execute the mandate in your user prompt."*
3. The orchestrator's invocation prompt *is* the private mandate.
4. Slice writes its artifact to `research/artifacts/<slice>-<topic>.md` and returns only a one-paragraph confirmation + file path.

This keeps the main thread's context clean (the orchestrator never sees the raw slice body unless it explicitly Reads it) and lets slices Read each other's artifacts when running sequentially.

### System prompt template for council-member subagents

```markdown
---
name: council-slice-<letter>
description: Research slice <letter> of the <topic> council. Use when the orchestrator requests slice-<letter> research.
tools: Read, Grep, Glob, WebSearch, WebFetch, Write
model: sonnet
---

You are Research Slice <letter> of a council of specialized researchers.

## Start every invocation by
1. Read `research/_council/brief.md` in full.
2. Read the user prompt carefully — it is your private mandate with
   success criteria and non-goals.
3. State your plan in one sentence before searching.

## Your output contract
Write exactly one markdown file to `research/artifacts/<slice>-<topic>.md`
using the council artifact template (frontmatter with slice, title,
word_count, confidence, key_claims, open_questions; then TL;DR; then
Key recommendations; then Body; then Sources).

## Hard constraints
- Stay within your mandate. If something belongs to another slice, note
  it in `open_questions` and move on.
- Cite every factual claim with a URL.
- Be opinionated. "X beats Y because Z" is required; both-sides hedging
  is not.
- Word count is a ceiling, not a floor.

## Return only
After writing the file, return a 2-3 sentence summary and the file path.
Do not paste the body into your response — it bloats the orchestrator's
context.
```

---

## 6. Orchestration topology for a 5–10 agent research council

**Parallel fan-out with a synthesis pass is the right default.** Anthropic found "3–5 subagents in parallel" cut research time up to 90% on independent investigations ([Anthropic multi-agent post](https://www.anthropic.com/engineering/multi-agent-research-system)). Sequential is justified only when slice N's output is *load-bearing input* for slice N+1 — rare in a research phase where you want diverse framings.

### Recommended topology

```
                  [ Orchestrator / Lead ]
                           │
          ┌────────┬───────┼───────┬────────┐
          ▼        ▼       ▼       ▼        ▼
       Slice A  Slice B  Slice C  Slice D  Slice E   (parallel)
          │        │       │       │        │
          └────────┴───────┼───────┴────────┘
                           ▼
                [ Synthesis / Critic pass ]   (sequential, reads all TL;DRs)
                           │
                           ▼
                    Final decision memo
```

- **Fan-out (parallel):** 5–10 independent slices, each with private mandate + shared-brief reference.
- **Synthesis pass (sequential, single agent):** reads every artifact's frontmatter + TL;DR. Drills into bodies only when TL;DRs conflict or flag `confidence: low`. Produces a decision memo.
- **Optional critic pass:** a separate subagent runs against the synthesis with a skeptic prompt, flagging unsupported claims. Cheap insurance against orchestrator groupthink.

### When to go sequential instead
- Slice B genuinely needs Slice A's taxonomy before it can frame its question.
- You are running on a token budget tight enough that Haiku-for-exploration is worth waiting for.
- A slice's output would drastically change the brief for the others (then restructure: make it Phase 1, rest is Phase 2).

### What NOT to do
- Don't nest subagents (Claude Code won't let you anyway — subagents can't spawn subagents).
- Don't let slices message each other. That's what agent teams are for, and agent teams are experimental (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, v2.1.32+, [Claude Code agent teams docs](https://code.claude.com/docs/en/agent-teams)). Filesystem handoff is sufficient for research.
- Don't dump peer slice artifacts into another slice's prompt preemptively. Let slices `Read` what they decide they need.

---

## Sources
- [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Claude Code — Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code — Orchestrate teams of Claude Code sessions (agent teams)](https://code.claude.com/docs/en/agent-teams)
- [Claude Agent SDK — Subagents](https://platform.claude.com/docs/en/agent-sdk/subagents)
- [Claude Agent SDK — Structured outputs](https://platform.claude.com/docs/en/agent-sdk/structured-outputs)
- [Cognition — Don't Build Multi-Agents](https://cognition.ai/blog/dont-build-multi-agents)
- [LangGraph — Memory (checkpointer + store)](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [LangChain — Structured output](https://docs.langchain.com/oss/python/langchain/structured-output)
- [Mastra — Structured output](https://mastra.ai/docs/agents/structured-output)
- [Simon Willison — Notes on Anthropic's multi-agent research system](https://simonwillison.net/2025/Jun/14/multi-agent-research-system/)
- [Vellum — Multi-agent systems with context engineering](https://vellum.ai/blog/multi-agent-systems-building-with-context-engineering)

## Implications for Our Project
- Build the council around **disk as shared state** (`research/_council/brief.md` + `research/artifacts/`). No LangGraph needed at this scale.
- Keep shared brief under ~1.5k tokens; put everything slice-specific in the invocation prompt.
- Standardize every artifact on the **frontmatter + TL;DR + body** template — orchestrator reads frontmatter and TL;DRs, drills in only on conflicts.
- Budget ~500k tokens for a full 8-slice pass on Sonnet 4.6; route exploration-only slices to Haiku 4.5.
- Default topology: **parallel fan-out → synthesis → optional critic**. Sequential only when one slice is a hard dependency of another.
