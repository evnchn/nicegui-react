**TL;DR** — When a `React(...)` element is constructed inside an **`async def` page handler**, the first (uncached) visit runs `npm install` + `vite build` synchronously **on the event loop**: the entire server — every user, every page — freezes until the build finishes. With a cold npm cache that's easily 30–60 s. Sync `def` handlers dodge this (Starlette's threadpool absorbs the blocking call), which makes it easy to miss in testing and nasty in production.

**Where** — `React.__init__` → `_ensure_built` → `subprocess.run(...)` in `_install_dependencies` / `_run_build` (react.py).

**Evidence** (v0.2.1, NiceGUI 3.14.0; app with a trivial `/ping` page and `/` doing a cold build in an async handler; `/ping` probed every 200 ms):

```
ping sent +0.05s latency 2.569s   ┐
ping sent +1.09s latency 1.520s   │ every request released at
ping sent +2.36s latency 0.264s   ┘ +2.61s = BUILD DONE
BUILD DONE at +2.61s
ping sent +2.75s latency 0.001s   ← loop free again
```

Control: the identical app with a sync `def` handler keeps `/ping` at ~2 ms throughout the build.

**Possible directions** (happy to PR whichever you'd prefer):
1. Minimal: detect a running event loop in `_ensure_built` and warn/fail loudly, pointing at `React.prebuild` (and document the pitfall in the README next to dev mode).
2. Nicer: render a placeholder immediately, run the build in a worker thread / background task, then push `bundle_url`/`css_urls` via `update()` when ready — the element-update channel already supports late prop pushes (dev reload uses exactly that path).

Found during a deeper agentic bughunt of v0.2.1; fuller notes on my fork's tracker: https://github.com/evnchn/nicegui-react/issues

🤖 Generated with [Claude Code](https://claude.com/claude-code)
