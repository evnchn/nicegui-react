# NiceGUI React Integration

Embed and interact with **React** components from **NiceGUI**, in Python.

`nicegui-react` builds your React project with [Vite](https://vitejs.dev/), serves the
compiled bundle as a static asset, and mounts it inside a native NiceGUI component. Props
flow from Python to React, and events flow from React back to Python - both over NiceGUI's
regular websocket channel.

## Features

- **Easy integration** - drop a React component into any NiceGUI page.
- **Reactive props** - update props from Python (timers, events, background tasks, bindings)
  and the React component re-renders immediately. This works in every mode, not just during
  development.
- **Events** - handle events emitted from React in your Python code (sync or async handlers).
- **Multiple components & instances per page** - render as many different React projects, and
  as many instances of each, on a single page as you like. Each bundle is isolated.
- **Automatic bundling** - your React code is built with Vite into a single, self-contained
  ES module.
- **Fast, content-addressed caching** - builds are skipped when nothing changed, and the served
  URL changes only when the bundle content changes, so browsers never serve a stale bundle.
- **Live reload (dev mode)** - edit your React code and see the change in the browser without
  restarting your Python app.

## Installation

```bash
pip install nicegui-react
```

## Requirements

- Python 3.8+
- NiceGUI 2.3+ (works with NiceGUI 2.x and 3.x)
- Node.js and npm (used to build the React project)

## Usage

```python
from nicegui import ui
from nicegui_react import React


@ui.page("/")
def index():
    with ui.card():
        ui.label("Here is the React component:")

        react = (
            React(
                react_project_path="./my_react_project",
                main_component="App",  # your main component's name
            )
            .props(title="Hello from Python!")
            .on("onClick", lambda data: ui.notify(f"React said: {data}"))
        )

        ui.button("Update from Python", on_click=lambda: react.props(title="Updated!"))


ui.run()
```

Your React component receives the props you pass from Python, plus a handler function for
every event you register with `.on(...)`:

```jsx
export default function App({ title, onClick }) {
  return (
    <div>
      <h3>{title}</h3>
      <button onClick={() => onClick({ clickedAt: Date.now() })}>Click me</button>
    </div>
  );
}
```

## Parameters

- `react_project_path` (str): path to your React project directory, resolved relative to the
  calling Python file.
- `main_component` (str): name of the main React component to render.
- `component_id` (str, optional): identifier for the component (defaults to the project folder
  name). Used to key the build cache.
- `env` (dict, optional): environment variables exposed to the React app at build time as
  `process.env.*`.
- `use_legacy_peer_deps` (bool, optional): pass `--legacy-peer-deps` to `npm install`.
- `dev` (bool, optional): enable development mode with live reload (see below).

## Methods

- `props(**kwargs)`: merge and update the props passed to the React component. Returns `self`
  for chaining.
- `on(event_name, handler)`: register a handler for an event emitted from React. The handler is
  called with the event payload. Returns `self` for chaining.
- `React.prebuild(react_project_path, main_component, ...)` (classmethod): build and cache a
  project ahead of time so the first page visit does not pay the build cost. Arguments match the
  constructor. Call it from `app.on_startup`:

```python
from nicegui import app
from nicegui_react import React

@app.on_startup
def _build_react():
    React.prebuild("./my_react_project", "App")
```

## Development mode (live reload)

Pass `dev=True` to build your project **in place** and watch it for changes. When you edit a
source file, Vite rebuilds and the component hot-reloads in the browser without a page refresh
(current props are preserved):

```python
React("./my_react_project", "App", dev=True)
```

In dev mode the following files are generated inside your project (add them to `.gitignore`):

```
.nicegui_react_dist/         # Vite build output
.nicegui_react/              # build metadata
_nicegui_react_main.jsx      # generated entry point
_nicegui_react_vite.config.mjs
package-lock.json            # if npm created it
```

In normal (non-dev) mode, none of these are written into your project. The build happens in a
cache directory under `~/.nicegui/react_cache/`.

## How it works

1. Your project is copied into a cache directory (or built in place in dev mode).
2. A small entry module and a Vite config are generated. The entry exports a `mount()` function
   and imports your component.
3. Vite builds a single, self-contained ES module (`bundle.js`) with React bundled in, plus a
   single `bundle.css`.
4. The bundle is served as a static file, and a native NiceGUI Vue component dynamically imports
   it and mounts your component into its own DOM element.
5. Props are passed as reactive component props; events are forwarded via the component's native
   event mechanism. No polling, no custom HTTP endpoints.

Because each component gets its own isolated bundle and its own element, any number of different
components and instances can coexist on one page.

## Setting up your React project

- Place your React project in a directory relative to your Python script.
- Your main component should be exported (default or named export both work).
- A `package.json` with `react`, `react-dom`, `vite` and `@vitejs/plugin-react` is recommended.
  If it is missing or incomplete, `nicegui-react` will fill in sensible defaults and run
  `npm install` for you.

See the [`examples/`](examples/) folder for a complete demo with two different React components,
multiple instances, timer-driven props, and events.

## Upgrading from 0.1.x

Version 0.2.0 rewrites the internals for performance and correctness while keeping the public API
(`React(...)`, `.props()`, `.on()`) unchanged. No changes are required to your Python code or your
React projects. Notable internal changes:

- The bundle now loads as an ES module instead of being injected inline over the websocket.
- Events use NiceGUI's native event system; the internal `/react_event/*` HTTP endpoint is gone.
- Builds run in production mode by default (smaller, faster bundles).
- Multiple different components and multiple instances per page are now supported.
- The wrapper element no longer uses `component_id` as its DOM `id` (this is what enables multiple
  instances). If you targeted that `id` from external CSS/JS, style your React component from within
  its own bundle instead.

## License

MIT. See the LICENSE file for details.

## Contributing

Contributions are welcome. Please fork the repository and open a pull request from a feature branch.
