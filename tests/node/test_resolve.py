import pytest


def test_resolve_module():
    from astdoc.node import resolve

    x = resolve("examples._styles.google")
    assert x == ("examples._styles.google", None)


def test_resolve_class():
    from astdoc.node import resolve

    x = resolve("examples._styles.google.ExampleClass")
    assert x == ("ExampleClass", "examples._styles.google")


def test_resolve_asname():
    from astdoc.node import resolve

    x = resolve("examples._styles.ExampleClassGoogle")
    assert x == ("ExampleClass", "examples._styles.google")


def test_resolve_attribute():
    from astdoc.node import resolve

    assert not resolve("examples._styles.ExampleClassGoogle.attr1")


def test_resolve_unknown():
    from astdoc.node import resolve

    assert not resolve("examples._styles.ExampleClassGoogle.attrX")


def test_resolve_none():
    from astdoc.node import resolve

    assert not resolve("x")


def test_resolve_jinja2():
    from astdoc.node import resolve

    x = resolve("jinja2.Template")
    assert x == ("Template", "jinja2.environment")


def test_resolve_astdoc():
    from astdoc.node import resolve

    x = resolve("astdoc.object.ast")
    assert x == ("ast", None)


def test_resolve_astdoc_class():
    from astdoc.node import resolve

    x = resolve("astdoc.object.ast.ClassDef")
    assert x == ("ClassDef", "ast")


@pytest.mark.parametrize(
    "name",
    ["astdoc", "astdoc.ast", "astdoc.ast.AST", "astdoc.ast.XXX"],
)
def test_get_fullname_module(name):
    from astdoc.node import get_fullname_from_module

    x = get_fullname_from_module(name, "astdoc.node")
    if "AST" in name:
        assert x == "ast.AST"
    elif "XXX" in name:
        assert not x
    else:
        assert x == name


def test_get_fullname_class():
    from astdoc.node import get_fullname_from_module

    x = get_fullname_from_module("Class", "astdoc.object")
    assert x == "astdoc.object.Class"
    assert get_fullname_from_module("ast", "astdoc.object") == "ast"
    x = get_fullname_from_module("ast.ClassDef", "astdoc.object")
    assert x == "ast.ClassDef"


@pytest.fixture(params=["", "._private", ".readonly_property"])
def attr(request):
    return request.param


def test_get_fullname_qualname(attr):
    from astdoc.node import get_fullname_from_module

    module = "examples._styles.google"
    name = f"ExampleClass{attr}"
    assert get_fullname_from_module(name, module) == f"{module}.{name}"


def test_get_fullname_qualname_alias(attr):
    from astdoc.node import get_fullname_from_module

    module = "examples._styles"
    name = f"ExampleClassGoogle{attr}"
    x = get_fullname_from_module(name, module)
    assert x == f"{module}.google.{name}".replace("Google", "")


def test_get_fullname_self():
    from astdoc.node import get_fullname_from_module

    name = "Class"
    module = "astdoc.object"
    assert get_fullname_from_module(name, module) == f"{module}.{name}"


def test_get_fullname_unknown():
    from astdoc.node import get_fullname_from_module

    assert not get_fullname_from_module("xxx", "astdoc.plugin")


def test_get_fullname_nested():
    from astdoc.node import get_fullname_from_module

    assert get_fullname_from_module("astdoc.doc.Item.name") == "astdoc.doc.Item.name"


def test_get_fullname_nested_none():
    from astdoc.node import get_fullname_from_module

    assert not get_fullname_from_module("astdoc.doc.Item.astdoc")


@pytest.mark.parametrize(
    ("name", "module", "expected"),
    [
        ("astdoc.doc.Item.clone", None, "astdoc.doc.Item.clone"),
        ("Item.clone", "astdoc.doc", "astdoc.doc.Item.clone"),
        ("Doc", "astdoc.object", "astdoc.doc.Doc"),
        ("Doc.clone", "astdoc.object", "astdoc.doc.Doc.clone"),
    ],
)
def test_get_fullname_method(name, module, expected):
    from astdoc.node import get_fullname_from_module

    assert get_fullname_from_module(name, module) == expected
