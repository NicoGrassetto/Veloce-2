---
to: tijn.goossens@portofantwerpbruges.com
subject: Follow-up — multi-agent architecture on Azure (Foundry + Microsoft Agent Framework)
---

Hi Tijn,

Thanks again for the conversation last week. As promised, a short follow-up with the architecture pointers and the reasoning behind the recommendation we discussed.

# Recommended shape

For where Port of Antwerp-Bruges is today, I'd anchor the multi-agent platform on two building blocks:

1. **Azure AI Foundry — prompt agents and hosted agents** as the managed runtime for individual agents.
   - Prompt agents are GA and ideal for the "configuration-only" agents (system prompt + tools + knowledge).
   - Hosted agents (currently public preview, but production-positioned) are the right home for agents that need custom code or a specific framework. Per-session VM isolation, scale-to-zero, Entra Agent ID, App Insights tracing and BYO VNet are built in. Docs: https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents
   - I'd **defer Foundry workflows** for now — they're newer/preview and the declarative model is still maturing. Easy to adopt later without rework.

2. **Microsoft Agent Framework (MAF)** as the orchestration SDK that ties agents together.
   - Repo: https://github.com/microsoft/agent-framework
   - Overview: https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-csharp
   - MAF is the open-source convergence of Semantic Kernel and AutoGen, in **both .NET and Python** with API parity — relevant given your .NET footprint.

# Why MAF instead of "one container per agent"

The container-per-agent topology gives you isolation and independent scaling, but it's a *deployment* pattern — it doesn't give you an agent model. You end up rebuilding orchestration, handoffs, shared memory, tracing, and identity yourself, on top of N ingresses and N scaling rules.

MAF gives you that layer out of the box:

- Built-in multi-agent orchestration patterns: sequential, concurrent, handoff, group-chat, magentic — as graph workflows with checkpointing, streaming, and human-in-the-loop.
- First-class agent / tool / middleware abstractions, MCP client, OpenTelemetry tracing, declarative YAML agents.
- Native interop with Foundry: a hosted or prompt agent can be wrapped as a MAF `AIAgent` and orchestrated in-process — so MAF and Foundry are complementary, not alternatives.
- Operationally much lighter: one orchestrator process running N agents in-proc, and you only externalise an agent into its own container (or Foundry hosted agent) when it genuinely needs its own scale, isolation, or lifecycle.

So the pragmatic rule: **start with MAF in one process; promote an agent to its own Foundry hosted agent or container the day it needs independent scale, a different runtime, or a different team owning it.**

# On autoscaling in a multi-agent setup — to be precise

You asked whether MAF has a built-in mechanism for autoscaling agents. The honest answer: **MAF is an SDK, not a runtime. It does not autoscale agents itself — the host does.** I'd rather be clear on that than oversell it.

What MAF *does* give you that matters for scale:

- Async, concurrent execution with fan-out / fan-in patterns, so a single orchestrator can drive many agents in parallel.
- Durable workflows with checkpointing, so long-running multi-agent runs survive process restarts.
- End-to-end OpenTelemetry, so when you do scale horizontally you keep distributed traces across agent hops.

Where autoscale actually comes from:

- The **orchestrator** runs on any autoscaling Azure compute — Container Apps, AKS, App Service, or Azure Functions — and scales the way those platforms already scale (KEDA / HPA / plan rules).
- **Foundry hosted agents** are themselves a managed, auto-scaled runtime: per-session VM-isolated sandboxes, scale-to-zero, stateful resume, no replica count to configure. See "Scaling and right-sizing" on the hosted agents page above.

So the architecture I'd recommend: MAF orchestrator on Container Apps (or AKS if you already standardise there), with heavy or independently-scaled agents offloaded to Foundry hosted agents. You get autoscale for the orchestrator from the platform, and autoscale per agent for free from Foundry.

# Why MAF rather than Pydantic AI

Pydantic AI is a good library and I want to be fair to it — strong typing, model-agnostic, MCP/A2A support, lightweight. For a small Python service it's a perfectly reasonable choice. For your context, MAF is the lower-risk fit, for a few specific reasons:

- **.NET and Python with parity.** Pydantic AI is Python-only. MAF supports both, which matters given your existing .NET landscape.
- **Multi-agent orchestration is in the box.** MAF ships sequential, concurrent, handoff, group-chat, and magentic patterns as first-class graph workflows. Pydantic AI's multi-agent guide explicitly positions it as a progression of *do-it-yourself* techniques (agent-as-tool, programmatic hand-off, raw graphs) — powerful, but more glue code you own and maintain.
- **First-party Microsoft alignment.** Roadmap tied to Azure AI Foundry, Microsoft 365 Copilot, Entra Agent ID, content safety and evals — and native wrapping of Foundry hosted/prompt agents as MAF agents.
- **Operational fit with what you already run.** OpenTelemetry to Application Insights is wired end-to-end (Foundry auto-injects the App Insights connection string into hosted agents). Pydantic AI's first-party observability path is Pydantic Logfire — a separate product/contract.
- **Governance.** Per-agent Entra identity, RBAC, content safety, evals, VNet isolation, and on-behalf-of for delegated permissions — all available through the Foundry + Entra path that MAF integrates with natively.

Net: Pydantic AI is fine for a small Python project. For a regulated, multi-team, .NET-and-Python multi-agent deployment on Azure with the identity and observability requirements PoAB has, MAF is the lower-friction choice and keeps you on a Microsoft-supported path.

# Suggested next step

Happy to set up a 45-minute working session with one of your architects to map two or three of your candidate agent use cases onto this shape (prompt agent vs hosted agent vs in-proc MAF agent), and to scope a 2-3 week PoC. Let me know what works in your calendar.

Best,
Nico
