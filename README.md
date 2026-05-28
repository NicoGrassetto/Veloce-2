<p align="center">
<pre align="center">
██╗   ██╗███████╗██╗      ██████╗  ██████╗███████╗
██║   ██║██╔════╝██║     ██╔═══██╗██╔════╝██╔════╝
██║   ██║█████╗  ██║     ██║   ██║██║     █████╗
╚██╗ ██╔╝██╔══╝  ██║     ██║   ██║██║     ██╔══╝
 ╚████╔╝ ███████╗███████╗╚██████╔╝╚██████╗███████╗
  ╚═══╝  ╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚══════╝
</pre>
</p>
<h1 align="center">Veloce</h1>

<p align="center">
  <b>Minimal AI-powered personal assistant that lives in your IDE.</b>
</p>

<p align="center">
  <a href="https://github.com/NicoGrassetto/Veloce/stargazers"><img src="https://img.shields.io/github/stars/NicoGrassetto/Veloce" alt="stars" /></a>
  <a href="https://github.com/NicoGrassetto/Veloce/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-AGPL--3.0-blue" alt="license" /></a>
  <img src="https://img.shields.io/static/v1?label=price&message=free&color=brightgreen" alt="free forever" />
</p>

<div align="center">
  <a href="https://veloce.dev/docs">Documentation</a>
  <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
  <a href="https://github.com/NicoGrassetto/Veloce/issues">Issues</a>
  <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
  <a href="https://github.com/NicoGrassetto/Veloce/issues?q=label%3Aroadmap">Roadmap</a>
  <br />
</div>

---

# What is Veloce?

Veloce is a fast, lightweight, AI-powered command-line assistant. It ships as a single binary called `vel`.

<p align="center">
  <img src=".github/assets/veloce-venn.svg" alt="Venn diagram showing Veloce as tech-agnostic, provider-agnostic, and customisable" width="720" />
</p>

It works **out of the box for $0** using local models — no API key required. When you need more power, plug in OpenAI, Anthropic, OpenRouter, or any OpenAI-compatible API. Bring your own provider, swap models on the fly, and keep full control over your setup.

## Background

In early spring 2026, my productivity hit an all-time high. I was heavily using a combination of Claude, Microsoft Copilot, Gemini, and ChatGPT in my day-to-day work, but it still was not feeling quite like I wanted it to.

I felt there was friction due to context switching. You see, switching from one tool to another, copy-pasting files and answers around, was the new roadblock in my productivity journey.

After a while, I found myself staying more and more within GitHub Copilot (or coding assistants more generally) because a coding assistant is all you need. It turns out that the paradigm we have converged to today (markdown, skills, agents as markdown, MCP, ...) is actually enough for most people, especially for a technical audience, because we have the advantage of full customisation.

So I built Veloce, merging most of my productivity tasks into this one repo template. I have been using it for a while now, and it is pretty good, so I thought I would share it. :)

Veloce means fast in Italian, which encompasses the spirit and values of this endeavor. Veloce works regardless of your productivity or tech stack and is meant to be customised.


# Getting started


# Project structure

```
.github/         Agents, skills, and Copilot instructions
knowledge/       Example inputs for agents to feed on (not produced outputs)
├── decks/       Example slide decks (Marp markdown, PPTX, PDF)
├── reports/     Example analytical reports and notebooks
├── articles/    Example long-form writing, blog posts, essays
└── assets/      Example images, charts, and supporting files
```

The `knowledge/` folder is **reference material**, not an output bin. Agents read from it to learn your tone, formatting, and structural preferences when producing new artefacts. Drop in examples of decks, reports, or articles you like, and agents will mirror that style.

### Contributing

Contributions are welcome! Veloce is community-driven and built in the open.

- Found a bug? [Open an issue](https://github.com/NicoGrassetto/Veloce/issues/new)
- Have an idea? [Start a discussion](https://github.com/NicoGrassetto/Veloce/issues/new)
- Want to contribute code? Fork the repo, make your changes, and open a PR

# Acknowledgements

Veloce builds on the excellent work of [Anthropic's skills](https://github.com/anthropics/skills/tree/main), which inspired the skill format and patterns used in this repo.

# License

AGPL-3.0 — see [LICENSE](LICENSE) for details.

Follow the [roadmap](https://github.com/NicoGrassetto/Veloce/issues?q=label%3Aroadmap) for updates.
