import ast

import pytest


def test_iter_imports():
    from astdoc.node import _iter_imports

    src = "import matplotlib.pyplot"
    node = ast.parse(src).body[0]
    assert isinstance(node, ast.Import)
    x = list(_iter_imports(node))
    assert len(x) == 2
    for i in [0, 1]:
        assert x[0][i] == "matplotlib"
        assert x[1][i] == "matplotlib.pyplot"
    src = "import matplotlib.pyplot as plt"
    node = ast.parse(src).body[0]
    assert isinstance(node, ast.Import)
    x = list(_iter_imports(node))
    assert len(x) == 1
    assert x[0][0] == "plt"
    assert x[0][1] == "matplotlib.pyplot"


def test_iter_imports_from():
    from astdoc.node import _iter_imports_from

    src = "from matplotlib import pyplot as plt"
    node = ast.parse(src).body[0]
    assert isinstance(node, ast.ImportFrom)
    x = list(_iter_imports_from(node, ""))
    assert len(x) == 1
    assert x[0][0] == "plt"
    assert x[0][1] == "matplotlib.pyplot"


def test_parse_import():
    from astdoc.node import Import, parse_node

    name = "test_parse_import"
    src = f"import {name}.b.c"
    node = ast.parse(src)
    x = list(parse_node(node, "m"))
    for k, n in enumerate(["", ".b", ".b.c"]):
        i = x[k][1]
        assert isinstance(i, Import)
        assert i.fullname == f"{name}{n}"
        assert x[k][0] == f"{name}{n}"


def test_parse_import_as():
    from astdoc.node import Import, parse_node

    src = "import a.b.c as d"
    node = ast.parse(src)
    x = parse_node(node, "m")[0]
    assert x[0] == "d"
    assert isinstance(x[1], Import)
    assert x[1].fullname == "a.b.c"


def test_parse_import_from():
    from astdoc.node import Import, parse_node

    src = "from x import a, b, c as C"
    node = ast.parse(src)
    x = list(parse_node(node, "m"))
    for k, n in enumerate("abc"):
        i = x[k][1]
        assert isinstance(i, Import)
        assert i.fullname == f"x.{n}"
        if k == 2:
            assert x[k][0] == "C"
        else:
            assert x[k][0] == n


@pytest.mark.parametrize("name", ["astdoc.node", "astdoc.renderer"])
def test_get_node_module(name: str):
    from astdoc.node import Module, get_node

    assert isinstance(get_node(name), Module)


@pytest.mark.parametrize("name", ["jinja2.Template", "astdoc.doc.Item"])
def test_get_node_class(name: str):
    from astdoc.node import Definition, get_node

    assert isinstance(get_node(name), Definition)


@pytest.mark.parametrize(
    ("name", "expected_repr"),
    [
        ("astdoc.node", "Module('astdoc.node')"),
        ("astdoc.renderer", "Module('astdoc.renderer')"),
        ("jinja2.Template", "Definition('Template', 'jinja2.environment')"),
        ("astdoc.doc.Item", "Definition('Item', 'astdoc.doc')"),
        ("astdoc.config.sys", "Import('sys')"),
    ],
)
def test_node_repr(name: str, expected_repr: str):
    from astdoc.node import get_node

    node = get_node(name)
    assert repr(node) == expected_repr


def test_parse_module_invalid():
    from astdoc.node import parse_module

    assert parse_module("invalid") == []


def test_get_node_invalid_module():
    from astdoc.node import get_node

    assert get_node("invalid") is None


def test_get_node_invalid_name():
    from astdoc.node import get_node

    assert get_node("invalid", "astdoc") is None
