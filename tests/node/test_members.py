import pytest


@pytest.mark.parametrize(
    "name",
    [
        "Template",
        "FileSystemLoader",
        "clear_caches",
        "Environment.compile",
        "ChoiceLoader.load",
    ],
)
def test_module_members_package_jinja(name):
    from astdoc.node import iter_module_members

    assert name in [m for m, _ in iter_module_members("jinja2")]


@pytest.mark.parametrize(
    "name",
    [
        "ExampleClassGoogle",
        "ExampleClassNumPy",
        "ExampleClassGoogle.readonly_property",
        "ExampleClassNumPy.readonly_property",
    ],
)
def test_module_members_package_alias(name):
    from astdoc.node import iter_module_members

    assert name in [m for m, _ in iter_module_members("examples._styles")]


def test_module_members_overloads():
    from astdoc.node import _iter_module_members, iter_module_members

    members = [m for m, _ in _iter_module_members("astdoc.utils")]
    assert members.count("cache") > 1

    members = [m for m, _ in iter_module_members("astdoc.utils")]
    assert members.count("cache") == 1


@pytest.mark.parametrize("name", ["Item.clone", "Section.clone", "Doc.clone"])
def test_module_members_class(name):
    from astdoc.node import iter_module_members

    assert name in [m for m, _ in iter_module_members("astdoc.doc")]


@pytest.mark.parametrize("private", [True, False])
def test_module_members_private(private: bool):
    from astdoc.node import iter_module_members

    members = [m for m, _ in iter_module_members("astdoc.utils", private=private)]

    assert any(m[0].startswith("_") for m in members) is private


@pytest.mark.parametrize("special", [True, False])
def test_module_members_special(special: bool):
    from astdoc.node import iter_module_members

    members = [m for m, _ in iter_module_members("astdoc.node", special=special)]

    assert any("__" in m for m in members) is special


@pytest.mark.parametrize(
    "module",
    ["astdoc.node", "astdoc.object", "examples._styles.google", "examples._styles"],
)
def test_module_members_have_objects(module: str):
    from astdoc.node import iter_module_members
    from astdoc.object import get_object

    members = iter_module_members(module, private=True, special=True)
    for m, _ in members:
        assert get_object(f"{module}.{m}") is not None


@pytest.mark.parametrize("name", ["Node", "Import", "Definition", "Assign", "Module"])
def test_iter_classes_from_module(name):
    from astdoc.node import iter_classes_from_module

    assert name in iter_classes_from_module("astdoc.node")


@pytest.mark.parametrize("name", ["Environment", "Template", "FileSystemLoader"])
def test_iter_classes_from_module_export(name):
    from astdoc.node import iter_classes_from_module

    assert name in iter_classes_from_module("jinja2")


@pytest.mark.parametrize("name", ["ExampleClassGoogle", "ExampleClassNumPy"])
def test_iter_classes_from_module_alias(name):
    from astdoc.node import iter_classes_from_module

    assert name in iter_classes_from_module("examples._styles")


def test_iter_functions_from_module():
    from astdoc.node import iter_functions_from_module

    functions = list(iter_functions_from_module("astdoc.node"))
    assert "resolve" in functions
    assert "get_fullname_from_module" in functions


def test_iter_methods_from_class():
    from astdoc.node import iter_methods_from_class

    assert "clone" in iter_methods_from_class("Doc", "astdoc.doc")


def test_iter_methods_from_class_property():
    from astdoc.node import iter_methods_from_class

    assert not list(iter_methods_from_class("Object", "astdoc.object"))


def test_get_module_members():
    from astdoc.node import get_module_members, iter_module_members

    x = list(iter_module_members("examples"))
    y = get_module_members("examples")
    assert len(x) == len(y)
    assert x[0][0] == "mod_a"
    assert y[0][0] == "ClassA"
    assert y[1][0] == "ClassA.method_a"
    assert y[2][0] == "ClassB"
    assert y[3][0] == "ClassB.method_b"
    assert y[-2][0] == "mod_c_alias"
    assert y[-1][0] == "sub"
