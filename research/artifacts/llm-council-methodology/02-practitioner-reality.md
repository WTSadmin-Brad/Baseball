# Practitioner Patterns: Shipping Multi-Agent LLM Research Systems (2024-2026)

**Slice B — practitioner patterns.** Raw output from a parallel research agent. Covers Anthropic's reference architecture, Cognition's counter-position, framework landscape, plan-and-execute vs ReAct vs Reflexion for research, and human-in-the-loop checkpoints. To be integrated into `research/artifacts/llm-council-methodology.md`.

---

## 1. Anthropic's Multi-Agent Research System — the reference architecture

Anthropic's June 2025 engineering post on their Research feature is the most detailed public description of a shipping multi-agent research system. The pattern:

- **Orchestrator-worker**: "a lead agent coordinates the process while delegating to specialized subagents that operate in parallel." The LeadResearcher analyzes the query, develops a strategy, and spawns workers.
- **Query decomposition**: The lead "decomposes queries into subtasks and describes them to subagents." Each subagent receives "an objective, an output format, guidance on the tools and sources to use, and clear task boundaries" — this explicit contract is what prevents duplicated work and coverage gaps.
- **Parallel dispatch (two levels)**: "(1) the lead agent spins up 3–5 subagents in parallel rather than serially; (2) the subagents use 3+ tools in parallel." This "cut research time by up to 90% for complex queries."
- **Synthesis**: After workers return, "the LeadResearcher synthesizes these results and decides whether more research is needed—if so, it can create additional subagents or refine its strategy." A separate **CitationAgent** post-processes for attribution.
- **Cost profile — the number to internalize**: "Agents typically use about 4× more tokens than chat interactions" and "Multi-agent systems use about 15× more tokens than chats." They only run it when "the value of the task is high enough to pay for the increased performance." The payoff: 90.2% improvement over single-agent Opus 4 on their internal research eval.
- **Key lessons**: simulate agents to debug prompts; teach orchestrators *explicit* delegation rules; embed effort-scaling heuristics ("simple fact → 1 subagent, 3–5 calls; complex research → 10+ subagents with divided responsibilities"); prioritize tool descriptions; let the model rewrite its own prompts; start broad then narrow.

Source: [How we built our multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system).

## 2. Cognition's counter-position — and when it applies

Walden Yan's "Don't Build Multi-Agents" (Cognition, 2025) argues multi-agent systems produce "fragile systems due to poor context sharing and conflicting decisions." Two principles:

1. **Agents must share full context** — complete traces, not summaries or isolated messages.
2. **Every action carries implicit decisions** that can conflict when parallel agents can't see each other's reasoning.

The archetypal failure: sub-agents build pieces of the same artifact (e.g., a Flappy Bird clone) with mismatched assumptions about style or API, and integration fails. Cognition's Devin is a coding agent editing a shared codebase — **the shared-mutable-state case where parallel workers genuinely collide**.

**Does this apply to our council?** No, mostly. Our agents produce *independent research documents*, not mutations to a shared artifact. The "implicit decisions conflict" failure mode requires shared state. Research artifacts are additive; conflicts surface at synthesis, which a lead agent resolves by reading full artifacts (not summaries).

**What we should steal from Yan anyway**: pass full artifacts, not bullet summaries, to the synthesizer; make each subagent's assumptions explicit in its output so the lead can reconcile them.

Sources: [Don't Build Multi-Agents (HN discussion)](https://news.ycombinator.com/item?id=45096962), [Single vs Multi-Agent System](https://www.philschmid.de/single-vs-multi-agents), [CTOL: AI Leaders Clash](https://www.ctol.digital/news/ai-leaders-clash-agent-architecture-cognition-anthropic-strategies/).

**Opinion**: Yan is right for coding agents, wrong as a universal rule. Anthropic is right for research. Our case is Anthropic's case.

## 3. Framework landscape — one line each

- **LangGraph** (LangChain): graph-based, explicit state, ships three named patterns — **supervisor** (central router), **swarm** (peer-to-peer handoffs), **hierarchical** (supervisors-of-supervisors). LangChain's 2025 State of AI Agents reports 57% of enterprise deployments now use multi-agent; supervisor + swarm dominate. [LangGraph hierarchical teams](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/), [langgraph-supervisor](https://github.com/langchain-ai/langgraph-supervisor-py).
- **CrewAI**: role/goal/backstory per agent, tasks with expected outputs, sequential or hierarchical process — opinionated and prescriptive, lowest ceremony for role-based teams.
- **AutoGen** (Microsoft): `GroupChat` with a manager selecting the next speaker — conversational, good for debate-style councils, weaker for deterministic pipelines.
- **OpenAI Swarm / Agents SDK**: lightweight handoffs via tool calls; no orchestration graph, agents pass control explicitly. Minimal, but you rebuild supervision yourself.

**Winner for our 5–10 agent research council**: We are running inside **Claude Code subagents**, which already give us orchestrator-worker semantics via the Agent tool. Don't adopt a framework — the Agent tool *is* our supervisor pattern. If we ever outgrow it, LangGraph's **supervisor** pattern is the closest conceptual match and the cleanest port. Swarm is wrong for research (no peer-to-peer need). Hierarchical is premature at 5–10 agents.

## 4. Plan-and-execute vs ReAct vs Reflexion for open-ended research

- **ReAct** (Thought → Action → Observation loop): lowest overhead, but re-plans every step. Strong for lookup-style tasks; weak when research has dependencies across many sub-questions.
- **Plan-and-execute** (ReWOO variant): plan the whole strategy up front, execute subtasks, re-plan if needed. "Works best for… a research project" per the dev.to comparison. This is what Anthropic's LeadResearcher does — plan decomposition, dispatch, then *conditionally* re-plan at synthesis.
- **Reflexion**: self-critique + persistent memory across trials. Valuable as a *post-hoc quality gate* on artifacts, not as the primary loop (too slow for breadth-first research).

**Winner for open-ended research**: **Plan-and-execute with a conditional re-plan step**, exactly Anthropic's pattern. ReAct belongs *inside* each subagent (it's how they use their tools); plan-and-execute is the *outer* orchestration. Reflexion is an optional critic agent you add when artifact quality matters more than latency.

Sources: [ReAct vs Plan-and-Execute (dev.to)](https://dev.to/jamesli/react-vs-plan-and-execute-a-practical-comparison-of-llm-agent-patterns-4gh9), [Agent Architectures: ReAct, Self-Ask, Plan-and-Execute](https://apxml.com/courses/langchain-production-llm/chapter-2-sophisticated-agents-tools/agent-architectures), [Reflexion Agent Pattern docs](https://agent-patterns.readthedocs.io/en/stable/patterns/reflexion.html).

## 5. Human-in-the-loop checkpoints — two concrete patterns

Shipping research systems pause at two predictable points:

1. **Post-plan, pre-dispatch approval.** After the lead decomposes the query into 3–5 subtasks, surface the plan to the human before burning tokens on parallel workers. LangGraph exposes this via `interrupt_before` on the supervisor node; Anthropic's Research UI shows the plan as it's being formed. This is the highest-leverage checkpoint: cheap to change a plan, expensive to redo 15× token spend.
2. **Pre-synthesis artifact review.** After subagents return but before the lead synthesizes, let the human kill/retry any weak artifact. Prevents one bad worker from poisoning the synthesis. CrewAI and LangGraph both support this via `human_input=True` on agent nodes or by pausing on the synthesis node.

**For our council**: bake in both. The plan-approval checkpoint costs nothing and prevents the most common research failure mode — the orchestrator misreading the question. The artifact-review checkpoint matches how a human reviewer already reads research before accepting it.

---

## Bottom line for the LLM Council

Adopt Anthropic's **orchestrator-worker + plan-and-execute + conditional re-plan** pattern, implemented on Claude Code's Agent tool. Cognition's critique doesn't bind us because our agents emit artifacts, not shared-state mutations — but honor its lesson by passing full artifacts (not summaries) into synthesis and requiring each subagent to make its assumptions explicit. Budget for ~15× chat token cost as a known ceiling. Gate on two human checkpoints: post-plan and pre-synthesis. Skip frameworks.

## Sources

- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/built-multi-agent-research-system)
- [Cognition: Don't Build Multi-Agents — HN thread](https://news.ycombinator.com/item?id=45096962)
- [Phil Schmid: Single vs Multi-Agent System](https://www.philschmid.de/single-vs-multi-agents)
- [CTOL: AI Leaders Clash Over Agent Architecture](https://www.ctol.digital/news/ai-leaders-clash-agent-architecture-cognition-anthropic-strategies/)
- [LangGraph Hierarchical Agent Teams](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/hierarchical_agent_teams/)
- [langgraph-supervisor](https://github.com/langchain-ai/langgraph-supervisor-py)
- [ReAct vs Plan-and-Execute](https://dev.to/jamesli/react-vs-plan-and-execute-a-practical-comparison-of-llm-agent-patterns-4gh9)
- [Agent Architectures: ReAct, Self-Ask, Plan-and-Execute](https://apxml.com/courses/langchain-production-llm/chapter-2-sophisticated-agents-tools/agent-architectures)
- [Reflexion Agent Pattern](https://agent-patterns.readthedocs.io/en/stable/patterns/reflexion.html)
