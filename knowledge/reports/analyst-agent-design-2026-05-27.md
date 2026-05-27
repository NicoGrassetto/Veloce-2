# Building an "Analyst" agent: research and design notes

_Researched 2026-05-27. Goal: inform a single `.agent.md` file in `.github/agents/` modeled on Microsoft 365 Copilot's Analyst agent, with a code-interpreter / data-analysis posture._

## TL;DR

Microsoft's Analyst agent is, at its core, a reasoning model (originally OpenAI's o3‑mini) wrapped around three things: a Python sandbox the model writes and re-runs code in, the user's tabular files (Excel/CSV) plus Microsoft Graph data, and a chain‑of‑thought loop that the user can watch step by step [1][2]. Every credible reference implementation in this space (Microsoft Foundry's Code Interpreter tool, Azure Container Apps dynamic sessions, LangChain's `SessionsPythonREPLTool`, OpenAI's Code Interpreter, E2B sandboxes) follows the same shape: an LLM that plans → writes Python → executes in an isolated sandbox with `pandas`/`matplotlib` preinstalled → observes results → refines, and finally returns a narrative answer plus generated artifacts (charts, tables, files) [3][4][5][6]. For a VS Code custom agent the sandbox layer is already present — Python notebook + terminal tools execute code in the workspace's interpreter — so the build reduces to a tightly-scoped `.agent.md` with the right tool allow-list and a methodology-shaped system prompt [7].

## Key findings

- Analyst is positioned as "a skilled data scientist": chain‑of‑thought reasoning over Python execution to go from raw spreadsheets to forecasts, visualizations, and revenue projections, with the generated code visible to the user for verification [1].
- The Researcher agent (same release) documents the methodology pattern Microsoft is standardizing on: clarify → plan → iterative reason/retrieve/review until marginal new insight `ΔI` falls below a threshold → synthesize with citations [2]. Analyst applies the same shape but the "retrieve" step is replaced by "execute Python on the data".
- All major code-interpreter offerings (Microsoft Foundry, Azure Container Apps dynamic sessions, OpenAI, E2B) standardize on Hyper-V or microVM isolation, a `/mnt/data` working directory, pre-installed scientific Python stack (`numpy`, `pandas`, `scikit-learn`, `matplotlib`), no outbound network by default, and a session lifetime measured in hours [3][4][5].
- For a workspace-local VS Code agent there is no need to provision any of that — `notebook_*`, `run_in_terminal`, and the Python environment tools already provide a sandboxed execution loop on the user's machine [7].
- The VS Code `.agent.md` format gives you exactly the levers needed to make this distinct from the default agent: `description` (drives picker matching), `argument-hint` (drives invocation), a tight `tools` allow-list, and optional `model` pinning [7].

## 1. What Microsoft 365 Copilot Analyst actually does

Analyst was announced alongside Researcher on 2025‑03‑25 and became generally available in June 2025 [1]. Microsoft describes it as a reasoning agent that "thinks like a skilled data scientist" — built on OpenAI's o3‑mini, optimized for advanced data analysis at work, using chain‑of‑thought reasoning to "progress through problems iteratively, taking as many steps as necessary to refine its reasoning" [1]. Distinctive properties versus generic Copilot Chat:

- **Writes and runs Python.** "It can run Python to tackle your most complex data queries — and you can view the code it's running in real time and check its work" [1]. The visible-code affordance is a deliberate trust mechanism.
- **Tabular‑data first.** Intended inputs are raw data scattered across spreadsheets; example outputs Microsoft cites are demand forecasts, visualizations of customer purchasing patterns, and revenue projections [1].
- **Reasoning model under the hood.** Unlike default Copilot Chat (which is a fast generalist), Analyst is gated on a slower deep-reasoning model; the tradeoff is depth/accuracy for latency.
- **Distinct from Researcher.** Researcher reasons over enterprise + web text (emails, meetings, docs, web pages) via a plan → retrieve → review → synthesize loop, citing on average ~10 sources per response [2]. Analyst's "retrieve" step is replaced by code execution against the user's data. Both share the same outer methodology.

There is no separate published Learn doc deep-dive on Analyst comparable to the Researcher engineering blog [2]; the 2025‑03‑25 announcement remains the primary source [1].

## 2. Architectural patterns for analyst-style agents

The architectural pattern is consistent across implementations:

```
user prompt + attached data
        │
        ▼
┌──────────────────────────┐
│  Plan (subquestions,     │
│  expected outputs)       │ ◄──── clarifying questions when ambiguous
└──────────────────────────┘
        │
        ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│  Write Python  ────────► │    │  Sandboxed kernel         │
│  (pandas/duckdb/...)     │    │  (Jupyter, ACA dynamic    │
│                          │ ─► │  sessions, E2B, Foundry   │
│  Observe stdout/result   │ ◄─ │  Code Interpreter, ...)   │
└──────────────────────────┘    └──────────────────────────┘
        │
        ▼     (loop until ΔInsight < ε or plan complete)
┌──────────────────────────┐
│  Synthesize: narrative + │
│  tables + charts +       │
│  caveats + citations to  │
│  the executed steps      │
└──────────────────────────┘
```

**Code execution backends.** Production-grade options share the same shape — isolated VM-class sandbox, `/mnt/data` working dir, scientific Python preinstalled, session identifier for state persistence across turns:

- **Microsoft Foundry Code Interpreter** is a managed agent tool that internally uses Azure Container Apps dynamic sessions; each session has a 1-hour active / 30-minute idle lifetime, runs untrusted Python in a Hyper‑V boundary, has no outbound network, and surfaces generated files via `container_file_citation` annotations the caller downloads [4].
- **Azure Container Apps dynamic sessions (code interpreter)** is the underlying primitive: per-session Hyper-V isolation, 220‑second per-execution cap, multipart file upload to `/mnt/data`, preinstalled `numpy`/`pandas`/`scikit-learn`, and first-party LangChain / LlamaIndex / Semantic Kernel integrations [3]. LangChain exposes it as `SessionsPythonREPLTool` from `langchain-azure-dynamic-sessions`, used in the official `langchain-python-webapi` sample [6].
- **E2B sandboxes** are an OSS-leaning alternative: per-request Linux microVMs created on demand, file upload/download, arbitrary command execution, template-based environment definition [5].
- **OpenAI / Foundry Assistants Code Interpreter** is the highest-level option: you pass file IDs at agent or run scope, the platform handles sandbox lifecycle, and file artifacts come back as annotations.

**Tabular data handling.** `pandas` is the default; `DuckDB` (in-process SQL over Parquet/CSV/Arrow) is the strongest second choice when datasets exceed pandas-friendly sizes or when users want SQL semantics. `Polars` is increasingly common for >1 GB workloads. The agent should pick based on size, not preference.

**Visualization.** `matplotlib` is the lingua franca because it serializes to PNG inside any sandbox; `plotly` is preferred when the output surface can render interactive HTML.

**Iterative plan → code → observe loop.** Two patterns dominate:
- **Single‑agent ReAct loop** (LangChain/LlamaIndex default): one LLM, tool calls in a loop, scratchpad in context. Simplest; works well up to ~10 steps.
- **Plan‑and‑execute with self‑critique** (AutoGen / Semantic Kernel / Researcher‑style): a planner produces a numbered plan, an executor runs each step, a critic checks each step's output and triggers replanning. Higher quality on long analyses, more tokens.

**Grounding sources.** Two grounding modes coexist:
1. **User-attached files** (CSV/XLSX/Parquet) — uploaded once, analyzed in-session. This is Analyst's primary mode.
2. **Connected data sources** (databases, semantic layer, M365 Graph) — surfaced as additional tools the agent can query; results land back in pandas for analysis.

**Verification / self‑critique steps.** The patterns that consistently improve quality:
- Always print `.shape`, `.dtypes`, `.head()`, and null counts before analysis — surfaces schema surprises early.
- Re‑derive any headline number two ways (e.g., groupby vs. pivot) and assert equality.
- For every chart, also emit the underlying table.
- Have the agent restate assumptions and known caveats at the end of every report.

## 3. Existing reference implementations

- **Microsoft Foundry Code Interpreter tool** — official Microsoft pattern; the Learn doc walks through uploading a CSV, asking for a bar chart, and downloading the PNG via `container_file_citation` [4].
- **Azure Container Apps dynamic sessions + LangChain sample** — `Azure-Samples/container-apps-dynamic-sessions-samples`, specifically `langchain-python-webapi/main.py`, shows the minimal three lines that wire a session-backed Python REPL into a tool-calling agent [6].
- **LangChain `langchain-azure-dynamic-sessions`** — published on PyPI; provides `SessionsPythonREPLTool` so any LangChain agent gets a managed Python sandbox without writing its own executor [3][6].
- **LlamaIndex `llama-index-tools-azure-code-interpreter`** and **Semantic Kernel** (`semantic-kernel >= 0.9.8-b1`) — equivalent integrations against the same ACA sessions backend [3].
- **E2B `code-interpreter-sdk` AI‑data‑analyst tutorial** — community reference showing the end-to-end loop with an alternative sandbox [5].
- **Microsoft 365 Researcher engineering blog** — not a code drop, but the most detailed public description of the plan / iterate / synthesize pattern Microsoft has shipped, directly applicable to Analyst-style design [2].

## 4. System prompt / instruction patterns that work for analyst agents

Across the implementations above, well-performing analyst prompts share a consistent skeleton:

1. **Persona & scope.** "You are a senior data analyst. You answer questions by writing and executing Python on the user's data. You never fabricate numbers."
2. **Available tools.** Enumerated explicitly with one‑line "use when…" rules. Pointing the model at the right tool is more reliable than letting it guess.
3. **Methodology / decision rules.** A short ordered procedure:
   - If the request is ambiguous, ask at most 1–3 clarifying questions before doing any work.
   - Inspect the data first: shape, dtypes, head, nulls. State what you see.
   - Plan the steps before writing code; show the plan.
   - Write small, runnable cells. Show the code before running it.
   - After each cell: inspect output, decide next step, surface any anomaly.
   - Re‑derive headline numbers two ways when they will appear in the final answer.
4. **Data hygiene rules.** "Never silently coerce types or drop nulls — show the count and ask." "Treat string-typed numerics as a finding, not a nuisance."
5. **Output format.** A reproducible structure: TL;DR (2–4 sentences) → Key findings (bullets) → Tables + charts inline → Methodology / steps taken → Caveats & open questions.
6. **When to stop.** "Stop when further analysis would not change the headline answer. Surface what you skipped."
7. **What not to do.** Don't speculate beyond the data, don't summarize without citing the cell that produced the number, don't fabricate column names.

This mirrors the Researcher engineering blog's emphasis on a planning phase, iterative review, and an explicit stop criterion when marginal insight drops [2].

## 5. Practical recommendations for a VS Code Analyst agent

VS Code custom agents are `.agent.md` Markdown files with YAML frontmatter, discovered automatically from `.github/agents/` in the workspace [7]. Key fields, all relevant here:

- `name` — display name in the picker (defaults to filename).
- `description` — shown as placeholder text and used by the model for "should I hand off to this agent?" decisions; phrase it as the trigger surface (when to invoke).
- `argument-hint` — placeholder text in the chat input, guides what the user types.
- `tools` — tool/tool‑set allow‑list; tools not listed are not available to the agent.
- `model` — single model name or a prioritized array; let you pin a reasoning model for this agent.
- `user-invocable` / `disable-model-invocation` — control whether it shows in the picker and whether other agents can subagent‑call it.
- `handoffs` — optional next‑step buttons (e.g., hand off to a writer agent).

The body of the file is the system prompt and gets prepended to every user message in the agent. Tool references in the body use `#tool:<tool-name>` syntax [7].

### Recommended frontmatter sketch

```yaml
---
name: Analyst
description: Analyzes tabular data (CSV/XLSX/Parquet) end-to-end — plans, writes Python, runs it in a notebook, and returns charts + narrative with cited cells. Use when the user attaches data or asks "analyze", "forecast", "summarize this spreadsheet", "what does this data say".
argument-hint: <paste a question about your data, or attach a .csv / .xlsx>
model:
  - GPT-5.2 (copilot)
  - Claude Opus 4.7 (copilot)
tools:
  # File + workspace inspection
  - read_file
  - file_search
  - grep_search
  - list_dir
  # Python execution loop (the core capability)
  - configure_python_environment
  - install_python_packages
  - get_python_environment_details
  - configure_notebook
  - create_new_jupyter_notebook
  - edit_notebook_file
  - run_notebook_cell
  - read_notebook_cell_output
  - copilot_getNotebookSummary
  - notebook_install_packages
  # Spreadsheet skill (already in this repo)
  - xlsx
  # Terminal fallback for non-Python data tools (duckdb CLI, etc.)
  - run_in_terminal
  - get_terminal_output
# Keep editing/git tools OFF — analyst should not mutate source code.
user-invocable: true
disable-model-invocation: false
---
```

Notes on the choices above:

- **Description first.** The phrasing — "when the user attaches data or asks 'analyze', 'forecast', 'summarize this spreadsheet'" — is the primary signal that determines whether the picker / model routes here instead of the default agent or a Researcher agent. Be explicit about file types and verbs.
- **Notebook over plain Python.** Notebook cells give you persistent kernel state across the plan→code→observe loop, which is exactly the affordance that makes Analyst's "iterative refinement" work. The `run_notebook_cell` + `read_notebook_cell_output` pair is the local equivalent of an ACA dynamic-session execution + result fetch.
- **Reuse the `xlsx` skill.** This repo already has a Marp-style skill pattern at `.github/skills/xlsx/SKILL.md`; the agent can invoke it for Excel-specific operations rather than re-implementing.
- **No edit / git tools.** Analyst should read data and produce notebooks/reports, not mutate the codebase. Omitting `replace_string_in_file`, `create_file` (other than report output), and version-control tools follows the least-privilege guidance in the VS Code docs [7].
- **Model selection.** Pin a reasoning-capable model as the first entry; fall back to a fast generalist. M365 Analyst uses o3‑mini specifically because chain-of-thought + tool use is its strength [1].

### Recommended system-prompt body outline (just sections)

The body of the `.agent.md` should contain these sections — keep each one short and concrete, the user (not this report) writes the prose:

1. **Persona** — one sentence: senior data analyst, writes and runs Python on the user's data, never fabricates numbers.
2. **When to ask clarifying questions** — cap at 3, only for ambiguous scope/metric/timeframe, otherwise proceed with stated assumptions.
3. **Methodology** — the ordered procedure (inspect → plan → code in cells → observe → refine → synthesize), explicitly mirroring the Researcher loop [2].
4. **Data hygiene rules** — no silent type coercion, surface nulls/dupes/outliers as findings, never invent column names, always show `.shape` + `.dtypes` first.
5. **Tooling rules** — which tool for which job: notebook for analysis, `xlsx` skill for Excel‑specific ops, `run_in_terminal` only for non-Python data tooling (e.g., DuckDB CLI). Reference tools as `#tool:run_notebook_cell` etc.
6. **Verification step** — re-derive headline numbers two ways before reporting; for every chart emit the underlying table.
7. **Output contract** — fixed report structure: TL;DR → Key findings (bullets) → Tables/charts inline → Methodology (numbered) → Caveats & open questions. Saved to `knowledge/reports/<slug>-<YYYY-MM-DD>.md` if it's a deliverable, otherwise inline.
8. **Stop criteria** — stop when further analysis won't change the headline; explicitly list what was skipped.
9. **What not to do** — no speculation beyond the data, no fabricated columns, no `pip install` without saying why, no mutating source files.

That gives you a single‑file agent that occupies the same conceptual slot as M365 Analyst in the M365 Copilot picker, but powered by the existing VS Code notebook + Python tooling — no extra sandbox infrastructure required.

## Open questions

- **Public Analyst engineering deep-dive.** Microsoft published a detailed engineering blog for Researcher [2] but not (yet) an equivalent for Analyst. Inferences about Analyst's internal loop are drawn from the Researcher pattern + the public announcement [1][2] rather than a primary Analyst engineering source.
- **OpenAI Code Interpreter primary doc.** The `platform.openai.com/docs/assistants/tools/code-interpreter` URL redirected during this run; the conceptual content was sourced via Microsoft Foundry's Code Interpreter doc [4], which uses the same sandbox model.
- **AutoGen current docs URL.** The previously-stable AutoGen code-executors page returned 404 during this run; the architectural pattern (planner + executor + critic) is cross-cited across LangChain / Foundry / Researcher sources but a current AutoGen URL was not retrieved.

## Sources

1. Spataro, J. — _Introducing Researcher and Analyst in Microsoft 365 Copilot_ — https://www.microsoft.com/en-us/microsoft-365/blog/2025/03/25/introducing-researcher-and-analyst-in-microsoft-365-copilot/ (Microsoft 365 Blog, 2025-03-25; notes Analyst is built on OpenAI o3‑mini, uses chain-of-thought reasoning, writes/runs Python, shows code to the user).
2. Anand, G. — _Researcher agent in Microsoft 365 Copilot_ — https://techcommunity.microsoft.com/blog/microsoft365copilotblog/researcher-agent-in-microsoft-365-copilot/4397186 (Microsoft 365 Copilot Blog, updated 2025-03-27; documents the plan / reason‑retrieve‑review / synthesize loop, the ΔI stop criterion, and the underlying OpenAI deep-research / o3 lineage).
3. _Serverless code interpreter sessions in Azure Container Apps_ — https://learn.microsoft.com/en-us/azure/container-apps/sessions-code-interpreter (Microsoft Learn, updated 2026-05-10; Hyper-V isolation, `/mnt/data`, preinstalled `numpy`/`pandas`/`scikit-learn`, LangChain / LlamaIndex / Semantic Kernel integrations, 220-sec execution cap, file upload/download API).
4. _Code Interpreter tool for Microsoft Foundry agents_ — https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/code-interpreter (Microsoft Learn, updated 2026-04-03; managed sandbox built on ACA dynamic sessions, 1-hour active / 30-minute idle session, CSV→bar chart sample, `container_file_citation` annotation pattern).
5. _E2B Documentation_ — https://e2b.dev/docs (E2B, retrieved 2026-05-27; per-sandbox isolated Linux VMs for agent code execution, SDK quickstart).
6. _Tutorial: Use code interpreter sessions in LangChain with Azure Container Apps_ — https://learn.microsoft.com/en-us/azure/container-apps/sessions-tutorial-langchain (Microsoft Learn, updated 2024-10-11; canonical `SessionsPythonREPLTool` + `langchain-azure-dynamic-sessions` wiring sample at `Azure-Samples/container-apps-dynamic-sessions-samples`).
7. _Custom agents in VS Code_ — https://code.visualstudio.com/docs/copilot/customization/custom-agents (VS Code Docs, updated 2026-05-20; `.agent.md` location `.github/agents/`, full frontmatter schema including `description`, `argument-hint`, `tools`, `model`, `user-invocable`, `disable-model-invocation`, `handoffs`).
