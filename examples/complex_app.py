"""A more complex nicegui-react demo.

The chart on the right is a React component (built on the third-party `recharts`
library, bundled automatically). The controls on the left are plain NiceGUI
widgets running in Python. Moving a control updates the React chart live, and
adding/removing metrics sends events from React back to Python.

Exercises: a third-party npm dependency, complex array/object props updating
live from Python, React-internal state (a controlled input) alongside
Python-driven props, and events with structured payloads.

Run with:  python examples/complex_app.py
"""
import math
import os
import random

from nicegui import ui

from nicegui_react import React

N = 40  # number of samples visible in the chart window


@ui.page('/')
def index() -> None:
    ui.label('nicegui-react — a live React chart, driven from Python').classes('text-2xl font-bold')
    ui.label(
        'The card on the right is a React component (recharts). The controls on the left are plain '
        'Python (NiceGUI). Change a control and the React chart reacts instantly; add or remove a '
        'metric and React sends an event back to Python.'
    ).classes('text-sm text-gray-500').style('max-width: 820px')

    state = {
        'waveform': 'Sine',
        'amplitude': 70,
        'noise': 5,
        'phase': 0.0,
        'series': [],
        'items': [{'id': 1, 'label': 'CPU load'}, {'id': 2, 'label': 'Memory'}],
        'next_id': 3,
    }

    def sample_at(phase: float) -> float:
        if state['waveform'] == 'Sine':
            base = math.sin(phase)
        elif state['waveform'] == 'Square':
            base = 1.0 if math.sin(phase) >= 0 else -1.0
        else:  # Triangle
            base = (2.0 / math.pi) * math.asin(math.sin(phase))
        value = 50 + (state['amplitude'] / 2) * base + random.uniform(-state['noise'], state['noise'])
        return round(max(0.0, min(100.0, value)), 1)

    # Seed the visible window so the chart is populated on first paint.
    for _ in range(N):
        state['series'].append({'t': round(state['phase'], 2), 'value': sample_at(state['phase'])})
        state['phase'] += 0.3

    dash: React  # assigned below; the closures below read it lazily

    def regenerate() -> None:
        """Recompute the whole visible window so a control change is reflected at once."""
        end = state['phase']
        state['series'] = [
            {'t': round(end - 0.3 * (N - 1 - i), 2), 'value': sample_at(end - 0.3 * (N - 1 - i))}
            for i in range(N)
        ]
        dash.props(series=state['series'], waveform=state['waveform'])

    with ui.row().classes('items-start gap-6 no-wrap'):
        with ui.card().classes('w-72'):
            ui.label('Controls · Python (NiceGUI)').classes(
                'text-xs font-semibold text-indigo-600 tracking-wide'
            ).style('text-transform: uppercase')
            ui.separator()
            ui.label('Waveform').classes('text-sm text-gray-600')
            ui.toggle(
                ['Sine', 'Square', 'Triangle'],
                value=state['waveform'],
                on_change=lambda e: (state.update(waveform=e.value), regenerate()),
            ).classes('wf-toggle').props('no-caps')
            ui.label('Amplitude').classes('text-sm text-gray-600 q-mt-sm')
            ui.slider(
                min=0, max=100, value=state['amplitude'],
                on_change=lambda e: (state.update(amplitude=e.value), regenerate()),
            ).classes('amp-slider').props('label')
            ui.label('Noise').classes('text-sm text-gray-600 q-mt-sm')
            ui.slider(
                min=0, max=30, value=state['noise'],
                on_change=lambda e: (state.update(noise=e.value), regenerate()),
            ).classes('noise-slider').props('label')

        with ui.column():
            dash = React('components/dashboard', main_component='Dashboard').props(
                title='Live signal',
                unit='%',
                waveform=state['waveform'],
                series=state['series'],
                items=state['items'],
            )

    def on_add(data) -> None:
        label = (data or {}).get('label', '').strip()
        if not label:
            return
        state['items'] = state['items'] + [{'id': state['next_id'], 'label': label}]
        state['next_id'] += 1
        dash.props(items=state['items'])
        ui.notify(f'Added: {label}')

    def on_remove(data) -> None:
        remove_id = (data or {}).get('id')
        state['items'] = [item for item in state['items'] if item['id'] != remove_id]
        dash.props(items=state['items'])

    dash.on('onAddItem', on_add)
    dash.on('onRemoveItem', on_remove)

    # Live data: append a new sample and scroll the window (Python -> React).
    def tick() -> None:
        state['phase'] += 0.3
        state['series'] = (state['series'] + [{'t': round(state['phase'], 2), 'value': sample_at(state['phase'])}])[-N:]
        dash.props(series=state['series'])

    ui.timer(0.4, tick)


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(port=int(os.environ.get('PORT', '8123')), reload=False)
