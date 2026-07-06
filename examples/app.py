"""Demo app for nicegui-react.

Shows two *different* React components on one page, two instances of the same
component, Python -> React reactivity via a timer, and React -> Python events.

Run with:  python examples/app.py
"""
import os
from datetime import datetime

from nicegui import ui

from nicegui_react import React


@ui.page('/')
def index() -> None:
    ui.label('nicegui-react demo').classes('text-2xl font-bold')

    counters = {}
    state = {'a': 0, 'b': 100}

    with ui.row():
        # Two instances of the SAME component (proves multi-instance support).
        counters['a'] = (
            React('components/counter', main_component='Counter')
            .props(title='Counter A', count=state['a'])
        )
        counters['b'] = (
            React('components/counter', main_component='Counter')
            .props(title='Counter B', count=state['b'])
        )
        # A DIFFERENT component on the same page (proves multi-component support).
        clock = React('components/clock', main_component='Clock').props(label='Server time')

    def make_increment(key: str):
        def handler(data):
            state[key] += (data or {}).get('delta', 1)
            counters[key].props(count=state[key])
            ui.notify(f'Counter {key.upper()} incremented from React -> {state[key]}')
        return handler

    counters['a'].on('onIncrement', make_increment('a'))
    counters['b'].on('onIncrement', make_increment('b'))

    with ui.row():
        def bump(key: str):
            state[key] += 1
            counters[key].props(count=state[key])

        ui.button('Increment A from Python', on_click=lambda: bump('a'))
        ui.button('Increment B from Python', on_click=lambda: bump('b'))

    # Python -> React reactivity in production mode: push a new time each second.
    ui.timer(1.0, lambda: clock.props(time=datetime.now().strftime('%H:%M:%S')))


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(port=int(os.environ.get('PORT', '8123')), reload=False)
