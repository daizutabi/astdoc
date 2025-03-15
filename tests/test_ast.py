import ast
import textwrap
from inspect import _ParameterKind

import pytest


@pytest.fixture(scope="module")
def child_nodes():
    from astdoc.ast import iter_child_nodes

    src = "a:int\nb=1\n'''b'''\nc='c'"
    node = ast.parse(src)
    return list(iter_child_nodes(node))


def test_iter_child_nodes_len(child_nodes):
    assert len(child_nodes) == 3


@pytest.mark.parametrize(("i", "doc"), [(0, None), (1, "b"), (2, None)])
def test_iter_child_nodes(child_nodes, i, doc):
    assert child_nodes[i].__doc__ == doc


def test_iter_parameters_none():
    from astdoc.ast import iter_parameters

    src = "def f(): pass"
    node = ast.parse(src).body[0]
    assert isinstance(node, ast.FunctionDef)
    assert list(iter_parameters(node)) == []


@pytest.fixture(scope="module")
def parameters():
    from astdoc.ast import iter_parameters

    src = "def f(a,/,b=1,*,c,d=1): pass"
    node = ast.parse(src).body[0]
    assert isinstance(node, ast.FunctionDef)
    return list(iter_parameters(node))


@pytest.mark.parametrize(
    ("i", "name", "default", "kind"),
    [
        (0, "a", None, _ParameterKind.POSITIONAL_ONLY),
        (1, "b", 1, _ParameterKind.POSITIONAL_OR_KEYWORD),
        (2, "c", None, _ParameterKind.KEYWORD_ONLY),
        (3, "d", 1, _ParameterKind.KEYWORD_ONLY),
    ],
)
def test_iter_parameters(parameters, i, name, default, kind):
    from ast import Constant

    from astdoc.ast import Parameter

    p = parameters[i]
    assert isinstance(p, Parameter)
    assert p.name == name
    if default is None:
        assert p.default is None
    else:
        assert isinstance(p.default, Constant)
        assert p.default.value == default
    assert p.kind == kind


def test_iter_raises():
    from astdoc.ast import iter_raises

    src = "def f():\n raise ValueError('a')\n raise ValueError\n"
    node = ast.parse(src).body[0]
    assert isinstance(node, ast.FunctionDef)
    raises = list(iter_raises(node))
    assert len(raises) == 1


def _expr(src: str) -> ast.expr:
    expr = ast.parse(src).body[0]
    assert isinstance(expr, ast.Expr)
    return expr.value


def _unparse(src: str) -> str:
    from astdoc.ast import StringTransformer

    return StringTransformer().unparse(_expr(src))


def test_expr_name():
    assert _unparse("a") == "__astdoc__.a"


def test_expr_subscript():
    assert _unparse("a[b]") == "__astdoc__.a[__astdoc__.b]"


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        ("a.b", "__astdoc__.a.b"),
        ("a.b.c", "__astdoc__.a.b.c"),
        ("a().b[0].c()", "__astdoc__.a().b[0].c()"),
        ("a(b.c[d])", "__astdoc__.a(__astdoc__.b.c[__astdoc__.d])"),
    ],
)
def test_expr_attribute(src, expected):
    assert _unparse(src) == expected


def test_expr_str():
    assert _unparse("list['X.Y']") == "__astdoc__.list[__astdoc__.X.Y]"


@pytest.mark.parametrize(
    ("i", "text", "is_identifier"),
    [
        (0, "x, ", False),
        (1, "a.b0", True),
        (2, "[", False),
        (3, "c", True),
        (4, "], y", False),
    ],
)
def test_iter_identifiers_bracket(i, text, is_identifier):
    from astdoc.ast import _iter_identifiers

    x = list(_iter_identifiers("x, __astdoc__.a.b0[__astdoc__.c], y"))
    assert x[i] == (text, is_identifier)


@pytest.mark.parametrize(
    ("i", "text", "is_identifier"),
    [(0, "a.b", True), (1, "()", False)],
)
def test_iter_identifiers_paren(i, text, is_identifier):
    from astdoc.ast import _iter_identifiers

    x = list(_iter_identifiers("__astdoc__.a.b()"))
    assert x[i] == (text, is_identifier)


@pytest.mark.parametrize(
    ("i", "text", "is_identifier"),
    [(0, "'ab'\n ", False), (1, "a", True)],
)
def test_iter_identifiers_lines(i, text, is_identifier):
    from astdoc.ast import _iter_identifiers

    x = list(_iter_identifiers("'ab'\n __astdoc__.a"))
    assert x[i] == (text, is_identifier)


@pytest.mark.parametrize(
    ("i", "text", "is_identifier"),
    [(0, "'ab'\n ", False), (1, "α.β.γ", True)],
)
def test_iter_identifiers_greek(i, text, is_identifier):
    from astdoc.ast import _iter_identifiers

    x = list(_iter_identifiers("'ab'\n __astdoc__.α.β.γ"))
    assert x[i] == (text, is_identifier)


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        ("a", "<a>"),
        ("a.b.c", "<a.b.c>"),
        ("a.b[c].d(e)", "<a.b>[<c>].d(<e>)"),
        ("a | b.c | d", "<a> | <b.c> | <d>"),
        ("list[A]", "<list>[<A>]"),
        ("list['A']", "<list>[<A>]"),
    ],
)
def test_unparse(src, expected):
    from astdoc.ast import unparse

    def callback(s: str) -> str:
        return f"<{s}>"

    def f(s: str) -> str:
        return unparse(_expr(s), callback)

    assert f(src) == expected


@pytest.mark.parametrize(
    ("src", "expected"),
    [("@classmethod\ndef func(cls): pass", True), ("def func(cls): pass", False)],
)
def test_is_classmethod(src, expected):
    from astdoc.ast import is_classmethod

    node = ast.parse(src).body[0]
    assert is_classmethod(node) is expected


@pytest.mark.parametrize(
    ("src", "expected"),
    [("@staticmethod\ndef func(): pass", True), ("def func(): pass", False)],
)
def test_is_staticmethod(src, expected):
    from astdoc.ast import is_staticmethod

    node = ast.parse(src).body[0]
    assert is_staticmethod(node) is expected


@pytest.mark.parametrize(
    ("src", "expected"),
    [("x: int = 5", True), ("x = 5", True), ("def func(): pass", False)],
)
def test_is_assign(src, expected):
    from astdoc.ast import is_assign

    node = ast.parse(src).body[0]
    assert is_assign(node) is expected


@pytest.mark.parametrize(
    ("src", "expected"),
    [("def func(): pass", True), ("class MyClass: pass", False)],
)
def test_is_function_def(src, expected):
    from astdoc.ast import is_function_def

    node = ast.parse(src).body[0]
    assert is_function_def(node) is expected


@pytest.mark.parametrize(
    ("src", "expected"),
    [("@property\ndef func(self): pass", True), ("def func(self): pass", False)],
)
def test_is_property(src, expected):
    from astdoc.ast import is_property

    node = ast.parse(src).body[0]
    assert is_property(node) is expected


@pytest.mark.parametrize(
    ("src", "expected"),
    [
        ("@property\n@func.setter\ndef func(self, value): pass", True),
        ("def func(self, value): pass", False),
    ],
)
def test_is_setter(src, expected):
    from astdoc.ast import is_setter

    node = ast.parse(src).body[0]
    assert is_setter(node) is expected


@pytest.mark.parametrize(
    ("name", "expected"),
    [("my_decorator", True), ("other_decorator", False)],
)
def test_has_decorator(name, expected):
    from astdoc.ast import has_decorator

    src = "@my_decorator\ndef func(): pass"
    node = ast.parse(src).body[0]
    assert has_decorator(node, name) is expected


def test_iter_child_nodes_import():
    from astdoc.ast import iter_child_nodes

    src = """
    import os
    class MyClass:
        def method(self): pass
    """
    node = ast.parse(textwrap.dedent(src))
    children = list(iter_child_nodes(node))
    assert len(children) == 2
    assert isinstance(children[0], ast.Import)
    assert isinstance(children[1], ast.ClassDef)


def test_get_assign_name_invalid():
    from astdoc.ast import get_assign_name

    src = "def func(): x = 1"
    node = ast.parse(src).body[0]
    assert get_assign_name(node) is None


def test_get_assign_type_type_alias():
    from astdoc.ast import TypeAlias, get_assign_type

    if not TypeAlias:
        return

    src = "type Vector = list[float]"
    node = ast.parse(src).body[0]
    assert isinstance(node, TypeAlias)
    type_ = get_assign_type(node)
    assert isinstance(type_, ast.Subscript)
    assert ast.unparse(type_) == "list[float]"


def test_parameter_repr():
    from astdoc.ast import Parameter

    param = Parameter(
        name="arg1",
        type=None,
        default=None,
        kind=_ParameterKind.POSITIONAL_OR_KEYWORD,
    )
    assert repr(param) == "Parameter('arg1')"


def test_has_decorator_invalid():
    from astdoc.ast import has_decorator

    src = "x=1"
    node = ast.parse(src).body[0]
    assert not has_decorator(node, "my_decorator", 0)


def test_iter_child_nodes_enum():
    from astdoc.ast import iter_child_nodes

    n = 2000
    src = "from enum import Enum, auto\nclass MyEnum(Enum):\n"
    vs = "".join(f"  VALUE_{i} = auto()\n" for i in range(n))
    src = f'{src}\n{vs}\n  """doc"""\n'
    node = ast.parse(src).body[1]
    nodes = list(iter_child_nodes(node))
    assert len(nodes) == n
    node = nodes[-1]
    assert isinstance(node, ast.Assign)
    target = node.targets[0]
    assert isinstance(target, ast.Name)
    assert target.id == "VALUE_1999"
    assert node.__doc__ == "doc"
