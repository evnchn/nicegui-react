**TL;DR** — On Windows the first build dies with `FileNotFoundError: [WinError 2]`: `subprocess.run(['npm', 'install'])` can't find `npm` because it's an `npm.cmd` shim and `CreateProcess` doesn't resolve `.cmd` from a bare name (no shell involved). Same for the `['npx', 'vite']` fallback, and `node_modules/.bin/vite` on Windows is the extensionless POSIX shim — `exists()` is true but it isn't executable. This PR resolves `npm`/`npx` via `shutil.which(...)` (honors `PATHEXT` on Windows, no-op on POSIX), prefers `node_modules/.bin/vite.cmd` on win32, and raises a clear "install Node.js" `RuntimeError` when nothing is found — which also improves the bare `FileNotFoundError` a missing Node currently produces on every platform.

**Honesty note** — no Windows box in this rig, so real-Windows execution was **not** tested; the change rests on documented `CreateProcess`/`PATHEXT`/`shutil.which` semantics. POSIX no-op was verified empirically.

<details>
<summary>Verification details (macOS)</summary>

- Cold build through the resolved-path code: cleared cache, ran `examples/app.py`, log shows a real `npm install` (`added 62 packages…`) and the page serves HTTP 200.
- REPL: with `shutil.which` monkeypatched to `None`, the `RuntimeError` raises with the Node.js pointer; unpatched, the resolved absolute npm path is used verbatim as `command[0]`.
- Win32 branch: with `sys.platform` monkeypatched and a temp `.bin/` containing both `vite` and `vite.cmd`, the win32 branch selects `vite.cmd`, the darwin branch selects the plain shim. (Throwaway REPL checks only — no test scaffolding in the diff.)

Found during a deeper agentic bughunt of v0.2.1 (`pyproject` classifies the package `OS Independent`, hence the PR); fuller notes on my fork's tracker: https://github.com/evnchn/nicegui-react/issues

</details>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
