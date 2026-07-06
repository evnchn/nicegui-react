"""A more complex nicegui-react demo.

Exercises: a third-party npm dependency (recharts) bundled into the component,
complex array/object props updating live from a timer, multiple events with
different payloads, an async Python event handler, and React-internal state
(a controlled input) coexisting with Python-driven props.

Run with:  python examples/complex_app.py
"""
import asyncio
import math
import os
import random

from nicegui import ui

from nicegui_react import React


@ui.page('/')
def index() -> None:
    ui.label('nicegui-react — complex example (live recharts dashboard)').classes('text-2xl font-bold')

    state = {
        'series': [{'t': i, 'value': round(55 + 20 * math.sin(i / 3), 1)} for i in range(20)],
        'items': [{'id': 1, 'label': 'CPU load'}, {'id': 2, 'label': 'Memory'}],
        'next_id': 3,
        'tick': 20,
    }

    dash = React('components/dashboard', main_component='Dashboard').props(
        title='Live Metrics',
        status='idle',
        series=state['series'],
        items=state['items'],
    )

    def sync() -> None:
        dash.props(series=state['series'], items=state['items'])

    def on_add(data) -> None:
        label = (data or {}).get('label', '').strip()
        if not label:
            return
        state['items'] = state['items'] + [{'id': state['next_id'], 'label': label}]
        state['next_id'] += 1
        sync()
        ui.notify(f'Added: {label}')

    def on_remove(data) -> None:
        remove_id = (data or {}).get('id')
        state['items'] = [item for item in state['items'] if item['id'] != remove_id]
        sync()
        ui.notify(f'Removed #{remove_id}')

    async def on_refresh(_data) -> None:
        # Async handler: show a loading state, do "work", then push fresh data.
        dash.props(status='loading')
        await asyncio.sleep(0.8)
        state['series'] = [{'t': i, 'value': random.randint(20, 95)} for i in range(20)]
        state['tick'] = 20
        dash.props(series=state['series'], status='idle')
        ui.notify('Chart refreshed (async)')

    dash.on('onAddItem', on_add)
    dash.on('onRemoveItem', on_remove)
    dash.on('onRefresh', on_refresh)

    # Live data: append a new point every second (Python -> React reactivity).
    def tick() -> None:
        t = state['tick']
        value = 55 + 25 * math.sin(t / 3) + random.uniform(-6, 6)
        state['series'] = (state['series'] + [{'t': t, 'value': round(value, 1)}])[-30:]
        state['tick'] = t + 1
        dash.props(series=state['series'])

    ui.timer(1.0, tick)


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(port=int(os.environ.get('PORT', '8123')), reload=False)
