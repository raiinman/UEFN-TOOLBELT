"""Offline Slate callback simulation for the reviewed local acceptance driver."""
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

DRIVER = Path(__file__).resolve().parents[1] / 'docs/audits/evidence/2026-10-09-toolbelt-acceptance/run_native_sections.py'


def load_driver(tmp_path, monkeypatch, results=None, nesting=False):
    unreal = ModuleType('unreal')
    unreal.log = lambda *_: None
    unregistered = []
    unreal.register_slate_post_tick_callback = lambda _: 'handle'
    unreal.unregister_slate_post_tick_callback = unregistered.append
    tb = ModuleType('UEFN_Toolbelt')
    tools = ModuleType('UEFN_Toolbelt.tools')
    suite = ModuleType('UEFN_Toolbelt.tools.integration_test')
    suite._acceptance_identity = lambda: {'project': 'ToolbeltAcceptance'}
    suite._SECTION_NAMES = ('materials', 'textures')
    tools.integration_test = suite
    calls = []
    driver = {}
    output = tmp_path / 'native-sections-r2'

    def original_run(tool, **kwargs):
        assert tool == 'toolbelt_integration_test'
        section = kwargs['sections'][0]
        recorded = json.loads((output / 'run.json').read_text(encoding='utf-8'))
        assert recorded['current_section'] == section
        assert recorded['in_progress'] is True
        calls.append(section)
        if nesting:
            for _ in range(250):
                driver['tick'](0.1)  # A tool pumps Qt/Slate events while it runs.
        response = (results or {}).get(section, {'status':'ok', 'completed':True})
        if isinstance(response, Exception):
            raise response
        return response

    tb.run = original_run
    for name, module in [('unreal', unreal), ('UEFN_Toolbelt', tb),
                         ('UEFN_Toolbelt.tools', tools),
                         ('UEFN_Toolbelt.tools.integration_test', suite)]:
        monkeypatch.setitem(sys.modules, name, module)
    source = DRIVER.read_text(encoding='utf-8')
    beginning = source.index('OUTPUT = Path(')
    ending = source.index('\n', beginning)
    source = source[:beginning] + f'OUTPUT = Path({str(output)!r})' + source[ending:]
    exec(compile(source, str(DRIVER), 'exec'), driver)
    driver['next_tick'] = 0
    return driver, calls, output, tb, original_run, unregistered


def test_nested_slate_callbacks_cannot_repeat_a_running_section(tmp_path, monkeypatch):
    driver, calls, output, tb, original, unregistered = load_driver(tmp_path, monkeypatch, nesting=True)
    driver['tick'](0.1)
    assert calls == ['materials']
    assert driver['busy'] is False
    driver['next_tick'] = 0
    driver['tick'](0.1)
    assert calls == ['materials', 'textures']
    driver['next_tick'] = 0
    driver['tick'](0.1)
    for _ in range(20):
        driver['tick'](0.1)
    state = json.loads((output / 'run.json').read_text(encoding='utf-8'))
    assert state['completed'] is True
    assert state['started_sections'] == ['materials', 'textures']
    assert len(state['results']) == 2
    assert state['in_progress'] is False
    assert calls == ['materials', 'textures']
    assert tb.run is original
    assert unregistered == ['handle']


@pytest.mark.parametrize('result', [{'status':'error', 'completed':False}, None,
                                   RuntimeError('fixture failure')])
def test_incomplete_or_raised_section_stops_without_retry(tmp_path, monkeypatch, result):
    driver, calls, output, tb, original, unregistered = load_driver(
        tmp_path, monkeypatch, results={'materials':result}, nesting=True)
    driver['tick'](0.1)
    for _ in range(20):
        driver['next_tick'] = 0
        driver['tick'](0.1)
    state = json.loads((output / 'run.json').read_text(encoding='utf-8'))
    assert calls == ['materials']
    assert state['completed'] is False
    assert state['stop_reason']
    assert state['in_progress'] is False
    assert tb.run is original
    assert unregistered == ['handle']
