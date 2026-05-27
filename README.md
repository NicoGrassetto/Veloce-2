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

## What is Veloce?

Veloce is a fast, lightweight, AI-powered command-line assistant. It ships as a single binary called `vel`.

It works **out of the box for $0** using local models — no API key required. When you need more power, plug in OpenAI, Anthropic, OpenRouter, or any OpenAI-compatible API. Bring your own provider, swap models on the fly, and keep full control over your setup.

```bash
vel ask "What is a goroutine?"       # one-shot question
vel chat                             # interactive conversation
vel summarize < article.txt          # summarize anything
vel transcribe meeting.mp3           # audio/video to text
echo '{"a":1}' | vel pipe            # pipe data through AI
```

Veloce is built around a few principles:

- **Fast** — parallel compute, optimized for speed
- **Lightweight** — minimal dependencies, small memory footprint
- **Free forever** — works locally at zero cost, always open-source
- **Open** — pluggable providers, MCP & A2A connectivity *(planned)*
- **Community-driven** — built in the open, shaped by contributors

## Install

```bash
# with go install (recommended)
go install github.com/NicoGrassetto/Veloce@latest
```

```bash
# with Homebrew (coming soon)
brew install veloce
```

```bash
# with install script (coming soon)
curl -fsSL https://veloce.dev/install | bash
```

```bash
# download binary (coming soon)
# grab the latest release from GitHub:
# https://github.com/NicoGrassetto/Veloce/releases
```

## Getting started

### 1. Ask a question

The fastest way to try Veloce — no setup needed if you have a local model running:

```bash
vel ask "Explain the difference between concurrency and parallelism"
```

### 2. Start a conversation

For back-and-forth dialogue:

```bash
vel chat
```

### 3. Pipe data through AI

Process stdin with AI — combine with any Unix tool:

```bash
cat error.log | vel pipe "Summarize the errors"
```

### Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `ask` | `vel ask [question]` | Ask a one-shot question |
| `chat` | `vel chat` | Start an interactive chat session |
| `cheer` | `vel cheer` | Get a motivational message |
| `create` | `vel create [resource]` | Create a new resource from a prompt |
| `extract` | `vel extract [source]` | Extract structured data from unstructured input |
| `index` | `vel index [path]` | Index files or directories for faster retrieval |
| `open` | `vel open [target]` | Open a file, URL, or application |
| `pipe` | `vel pipe` | Pipe stdin through Veloce for processing |
| `search` | `vel search [query]` | Search your laptop for files or directories |
| `speak` | `vel speak` | Talk to Veloce using your voice instead of text |
| `summarize` | `vel summarize [text]` | Summarize the given text |
| `tag` | `vel tag [input]` | Tag or label content with metadata |
| `transcribe` | `vel transcribe [file]` | Transcribe audio or video to text |
| `transform` | `vel transform [input]` | Transform content from one format to another |

### Built-in tools

Veloce comes with tools the AI can use autonomously during a session:

- **File ops** — `read`, `write`, `edit`, `list`, `glob`
- **Search** — `grep`, `websearch`
- **Web** — `webfetch`
- **System** — `bash`
- **Tasks** — `todoread`, `todowrite`

## Contributing

Contributions are welcome! Veloce is community-driven and built in the open.

- Found a bug? [Open an issue](https://github.com/NicoGrassetto/Veloce/issues/new)
- Have an idea? [Start a discussion](https://github.com/NicoGrassetto/Veloce/issues/new)
- Want to contribute code? Fork the repo, make your changes, and open a PR

## License

AGPL-3.0 — see [LICENSE](LICENSE) for details.

## FAQ

<details>
<summary><b>Is Veloce really free?</b></summary>
<br>
Yes, forever. Veloce is open-source and ships with support for local models that run on your machine at zero cost. You can optionally connect paid APIs like OpenAI or Anthropic, but it's never required.
</details>

<details>
<summary><b>Which AI models does it support?</b></summary>
<br>
Out of the box: local models (Ollama and others), OpenAI, Anthropic, and OpenRouter. Any OpenAI-compatible API endpoint also works. The provider system is pluggable — adding new providers is straightforward.
</details>

<details>
<summary><b>Can I use it offline?</b></summary>
<br>
Yes. With a local model running (e.g. via Ollama), Veloce works fully offline with no internet connection needed.
</details>

<details>
<summary><b>How do I add my own provider?</b></summary>
<br>
Veloce's provider system is designed to be pluggable. Provider implementations live in <code>internal/providers/</code>. Documentation for writing custom providers is coming soon.
</details>

<details>
<summary><b>What's on the roadmap?</b></summary>
<br>

- MCP server connectivity
- A2A agent support
- TUI mode with conversation history
- IDE integration
- Custom user-defined actions and flags
- Project tagging and management
- Semantic conversation search

Follow the [roadmap](https://github.com/NicoGrassetto/Veloce/issues?q=label%3Aroadmap) for updates.
</details>
