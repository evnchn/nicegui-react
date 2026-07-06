**TL;DR** — Two `React(...)` instances pointing at the **same project directory** but different `main_component` (or `env`/`dev`/`use_legacy_peer_deps`) collide on one cache key, so the second instance silently renders the first instance's component — no error anywhere. This PR includes the per-instance build configuration that was missing from the cache key, and makes `dev=True` fail loudly when a project dir is asked for two configurations at once (in-place builds share one entry/config/output per directory, so they cannot support that yet).

**Minimal repro** (v0.2.1, NiceGUI 3.14.0, Node 22):

```python
@ui.page('/')
def index():
    React('components/duo', main_component='CompA').props(label='(first)')
    React('components/duo', main_component='CompB').props(label='(second)')
```

with `src/CompA.jsx` / `src/CompB.jsx` each rendering a distinctive string. Browser-observed:

| before | after (this PR) |
|---|---|
| ![both instances render CompA](https://raw.githubusercontent.com/evnchn/nicegui-react/pr8-assets/before.png) | ![each instance renders its own component](https://raw.githubusercontent.com/evnchn/nicegui-react/pr8-assets/after.png) |

**Why** — `_generate_unique_hash` was `md5(component_id + path)` with `component_id` defaulting to the folder name; the in-process `React._bundles` registry early-returns on that key before the on-disk fingerprint (which *does* include `main_component`) is ever consulted, and both instances share one static mount path.

**Note** — existing dirs under `~/.nicegui/react_cache` become orphans and rebuild once under the new keys.

<details>
<summary>Verification details (all browser-verified via Playwright)</summary>

- **Cache reuse preserved**: two instances with the *same* `main_component` produce exactly one new cache dir (not two).
- **Regression**: bundled `examples/app.py` still serves; both counters + clock render, React→Python and Python→React paths work, no console errors.
- **Dev guard**: two `dev=True` instances with different `main_component` on one project dir now raise
  `RuntimeError: nicegui-react: dev=True builds in place, so each project directory supports only one configuration (main_component/env/flags) at a time. …`
  instead of silently rendering the wrong component (page 500s with a clear server-log message). A single `dev=True` instance still builds in place and renders correctly. Making dev builds fully per-configuration (per-hash entry/config/dist names) is left as a follow-up — happy to take a swing at it in a separate PR if you're interested.

A few smaller findings from the same review are tracked on my fork's issue list, in case any are of interest: https://github.com/evnchn/nicegui-react/issues

</details>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
