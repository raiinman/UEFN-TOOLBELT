"""Dashboard reopening must foreground hidden, visible and minimized windows."""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

SOURCE = Path('Content/Python/UEFN_Toolbelt/dashboard_pyside6.py')


@pytest.mark.parametrize('state', ['hidden', 'visible', 'minimized'])
def test_reopen_brings_dashboard_forward(monkeypatch, state):
    class Window:
        visible = state != 'hidden'
        minimized = state == 'minimized'
        raised = False
        active = False

        def isHidden(self):
            return not self.visible

        def isMinimized(self):
            return self.minimized

        def show(self):
            self.visible = True

        def showNormal(self):
            self.visible = True
            self.minimized = False

        def raise_(self):
            self.raised = self.visible and not self.minimized

        def activateWindow(self):
            self.active = self.raised and not self.minimized

    window = Window()
    namespace = {'_WINDOW': window, '_ensure_app': lambda: True,
                 'unreal': SimpleNamespace(log=lambda message: None)}
    monkeypatch.setitem(sys.modules, 'UEFN_Toolbelt', SimpleNamespace(run=lambda name: None))
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    function = next(node for node in tree.body
                    if isinstance(node, ast.FunctionDef) and node.name == 'launch_dashboard')
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(SOURCE), 'exec'), namespace)
    namespace['launch_dashboard']()
    assert window.visible and not window.minimized
    assert window.raised and window.active


def test_dashboard_does_not_cover_normal_tool_windows():
    # Real Qt flags, when available; this does not claim live Windows stacking acceptance.
    qtcore = pytest.importorskip('PySide6.QtCore')
    qtwidgets = pytest.importorskip('PySide6.QtWidgets')
    app = qtwidgets.QApplication.instance() or qtwidgets.QApplication([])
    window = qtwidgets.QMainWindow()
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    dashboard = next(node for node in tree.body
                     if isinstance(node, ast.ClassDef) and node.name == 'ToolbeltDashboard')
    constructor = next(node for node in dashboard.body
                       if isinstance(node, ast.FunctionDef) and node.name == '__init__')
    flags = next(node for node in constructor.body
                 if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                 and isinstance(node.value.func, ast.Attribute)
                 and node.value.func.attr == 'setWindowFlags')
    namespace = {'self': window, 'Qt': qtcore.Qt}
    try:
        exec(compile(ast.Module(body=[flags], type_ignores=[]), str(SOURCE), 'exec'), namespace)
        assert window.windowType() == qtcore.Qt.Window
        assert not window.windowFlags() & qtcore.Qt.WindowStaysOnTopHint
        assert not window.windowFlags() & qtcore.Qt.WindowStaysOnBottomHint
    finally:
        window.close()
        app.processEvents()
