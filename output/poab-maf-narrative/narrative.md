# Multi-agent on Azure — narrative material for Port of Antwerp-Bruges follow-up

_Researched 2026-05-28. Source-backed talking points; not the email itself._

## 1. Why Microsoft Agent Framework (MAF) instead of "one container per agent"

Microsoft Agent Framework is the **direct, open-source successor of Semantic Kernel + AutoGen**, built by the same teams and released for both **.NET and Python** with consistent APIs. It is positioned explicitly for teams "taking agents from prototype to production" and ships the agent abstractions, orchestration patterns, and operational plumbing you'd otherwise hand-roll around N independent containers. See the [MAF GitHub README](https://github.com/microsoft/agent-framework) and the [MS Learn overview](https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-csharp) ("Agent Framework is the next generation of both Semantic Kernel and AutoGen").

Concrete reasons MAF beats a "container per agent" topology:

- **Built-in multi-agent orchestration.** Graph-based workflows with sequential, concurrent, handoff, and group-collaboration patterns, plus checkpointing, streaming, human-in-the-loop, and time-travel — out of the box ([README, Key Features](https://github.com/microsoft/agent-framework#key-features)).
- **First-class agent + tool + middleware abstractions.** Tool calling, MCP clients, middleware pipelines, declarative (YAML) agents, agent skills, OpenTelemetry tracing — all in one SDK ([README](https://github.com/microsoft/agent-framework)).
- **Native interop with Azure AI Foundry.** A Foundry hosted agent or prompt agent can be wrapped as a MAF `AIAgent` and orchestrated locally or in-process (`AIProjectClient(...).AsAIAgent(...)` in .NET, `FoundryChatClient` in Python) — so MAF and Foundry are complementary, not competing ([MAF README — Foundry Hosted Agents](https://github.com/microsoft/agent-framework#key-features), [MAF overview](https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-csharp)).
- **Lower operational surface.** One orchestrator process running N agents in-proc vs. N containers + N ingresses + N scaling rules + N network hops + N identities. You only externalise an agent when it genuinely needs its own scale, isolation, or lifecycle.
- **Language parity and enterprise support path.** C# **and** Python with the same model; MIT-licensed, 10k+ stars, 86 releases, Microsoft-backed roadmap aligned with Foundry, Copilot SDK, and Entra Agent ID ([repo home](https://github.com/microsoft/agent-framework)).

"One container per agent" is a deployment topology, not an agent framework — it gives you isolation and scale primitives but forces you to reinvent orchestration, shared memory, tracing, and handoffs. MAF gives you the orchestration; Foundry / Container Apps / AKS give you the isolation when you actually need it.

## 2. Does MAF auto-scale agents in a multi-agent architecture?

Short answer: **no — MAF is an SDK, not a runtime. Autoscaling comes from the host.** This is the correct, honest framing for the customer.

What MAF *does* give you that matters for scale:

- **Async, concurrent agent execution** with fan-out / fan-in orchestration patterns (concurrent, group chat, handoff) in the workflow engine ([README, Orchestration Patterns & Workflows](https://github.com/microsoft/agent-framework#key-features)).
- **Durable workflows with checkpointing**, so long-running multi-agent runs survive process restarts and can resume ([Workflows samples — .NET](https://github.com/microsoft/agent-framework/tree/main/dotnet/samples/03-workflows), [Python](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows); see also Durable Task / Azure Functions hosting samples under [`04-hosting`](https://github.com/microsoft/agent-framework/tree/main/python/samples/04-hosting)).
- **Built-in OpenTelemetry**, so when you do scale horizontally you have distributed traces across agent hops ([Observability samples](https://github.com/microsoft/agent-framework#key-features)).
- **Delegation to Foundry hosted agents**, which *are* a managed, auto-scaled runtime — sessions run in per-session VM-isolated sandboxes that scale on demand with **scale-to-zero and stateful resume**, with no replica count to configure ([Hosted agents — Scaling and right-sizing](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents#scaling-and-right-sizing)).

So the recommended framing: **host the MAF orchestrator on any autoscaling Azure compute (Container Apps, AKS, App Service, Azure Functions), and offload heavy or independently-scaled agents to Foundry hosted agents, which give you per-session autoscale for free.**

## 3. Why MAF over Pydantic AI specifically

[Pydantic AI](https://pydantic.dev/docs/ai/overview/) is a genuinely good, lightweight, model-agnostic Python agent library with strong type-safety, capabilities, MCP/A2A support, and durable execution. For a small Python service, it's a fine choice and we'd say so. For a multi-agent, multi-team enterprise deployment at a port authority, the differentiators that matter:

- **.NET + Python, not Python-only.** Pydantic AI is [Python-only](https://pydantic.dev/docs/ai/overview/); MAF ships first-class C# and Python with parity ([MAF README](https://github.com/microsoft/agent-framework)). Material for a .NET-heavy operator.
- **Built-in multi-agent orchestration patterns.** MAF ships sequential, concurrent, handoff, group-chat, and magentic patterns as graph workflows. Pydantic AI's [Multi-Agent Patterns guide](https://pydantic.dev/docs/ai/guides/multi-agent-applications/) explicitly positions multi-agent as a progression of *do-it-yourself* techniques (agent-as-tool delegation, programmatic hand-off, raw graphs) — powerful but more assembly required.
- **First-party Microsoft alignment.** Roadmap tied to Azure AI Foundry, Microsoft 365 Copilot, Entra Agent ID, Microsoft Foundry content safety and evals; native wrapping of Foundry hosted/prompt agents as MAF agents ([MAF overview](https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-csharp), [Foundry agents overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview)).
- **Observability path the customer's ops team already runs.** OpenTelemetry + Application Insights are wired in end-to-end (Foundry auto-injects the App Insights connection string into hosted agents) ([Hosted agents — Observability](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents#observability)). Pydantic AI's first-party observability story is Pydantic Logfire (also OTel — works, but a separate product/contract).
- **Governance.** Per-agent Microsoft Entra identity, RBAC, content safety, evals, virtual-network isolation, OBO for delegated permissions — all available via the Foundry + Entra path that MAF integrates with ([Foundry overview — Enterprise capabilities](https://learn.microsoft.com/en-us/azure/foundry/agents/overview#enterprise-capabilities), [Hosted agents — Agent identity and endpoint](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents#agent-identity-and-endpoint)).
- **Durable, long-running stateful runs** are a built-in MAF concept (Durable Workflows, Durable Agents samples). Pydantic AI offers [durable execution](https://pydantic.dev/docs/ai/overview/) too, but typically through third-party engines (Temporal, etc.) rather than a native Microsoft-supported runtime.

Net: Pydantic AI is excellent for small Python projects. For a regulated, .NET-and-Python, multi-agent Azure deployment with enterprise identity/observability requirements, MAF is the lower-risk, lower-glue-code choice.

## 4. Quick confirmation on the Foundry guidance

To be precise with the customer, per the [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview#agent-types) (last updated 2026-04-29) and the [Hosted agents concept page](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents#limits-pricing-and-availability-preview):

- **Prompt agents — generally available.** No preview tag; recommended path for "rapid prototyping, internal tools, and agents that don't need custom orchestration logic."
- **Hosted agents — public preview**, but production-positioned: framework-of-your-choice (MAF, LangGraph, custom), 20 Azure regions including West Europe-adjacent (Sweden Central, Germany West Central, Switzerland North, Spain Central, France Central, Poland Central, Norway East), per-session VM isolation, Entra agent identity, App Insights tracing, BYO VNet.
- **Workflow agents — public preview**, newer; declarative YAML / visual builder for multi-step orchestration. Reasonable to defer until they GA or until you have a use case that benefits from the visual/no-code authoring model.

So the recommendation we'd give Port of Antwerp-Bruges today is accurate **with one caveat**: prompt agents are GA; hosted agents are preview-but-recommended; workflows are preview-and-defer. If the customer's procurement requires GA-only services, that's the point to surface.

## Sources

1. [microsoft/agent-framework — GitHub README](https://github.com/microsoft/agent-framework) (Microsoft, accessed 2026-05-28)
2. [Microsoft Agent Framework overview — MS Learn](https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-csharp) (Microsoft, 2026-04-06)
3. [What are hosted agents? — Azure AI Foundry docs](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/hosted-agents) (Microsoft, 2026-05-23)
4. [What is Microsoft Foundry Agent Service? — overview & agent types](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) (Microsoft, 2026-04-29)
5. [Pydantic AI — overview](https://pydantic.dev/docs/ai/overview/) (Pydantic Services, accessed 2026-05-28)
6. [Pydantic AI — Multi-Agent Patterns](https://pydantic.dev/docs/ai/guides/multi-agent-applications/) (Pydantic Services, accessed 2026-05-28)
