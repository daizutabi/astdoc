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


def test_resolve_mkdocs():
    from astdoc.node import resolve

    x = resolve("mkdocs.config.Config")
    assert x == ("Config", "mkdocs.config.base")


def test_resolve_astdoc():
    from astdoc.node import resolve

    x = resolve("astdoc.object.ast")
    assert x == ("ast", None)


def test_resolve_astdoc_class():
    from astdoc.node import resolve

    x = resolve("astdoc.object.ast.ClassDef")
    assert x == ("ClassDef", "ast")


def test_resolve_astdoc_module_plugin():
    from astdoc.node import resolve

    module = "astdoc.plugin"
    x = resolve("astdocPlugin", module)
    assert x == ("astdocPlugin", module)
    x = resolve("MkDocsConfig", module)
    assert x == ("MkDocsConfig", "mkdocs.config.defaults")


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


def test_get_fullname_jinja2():
    from astdoc.node import get_fullname_from_module

    x = get_fullname_from_module("jinja2.Template", "mkdocs.plugins")
    assert x == "jinja2.environment.Template"


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

    name = "astdocPlugin"
    module = "astdoc.plugin"
    assert get_fullname_from_module(name, module) == f"{module}.{name}"


def test_get_fullname_unknown():
    from astdoc.node import get_fullname_from_module

    assert not get_fullname_from_module("xxx", "astdoc.plugin")
    assert not get_fullname_from_module("jinja2.unknown", "mkdocs.plugins")


def test_get_fullname_plugin():
    from astdoc.node import get_fullname_from_module

    module = "astdoc.plugin"
    x = get_fullname_from_module("MkDocsConfig", module)
    assert x == "mkdocs.config.defaults.MkDocsConfig"
    x = get_fullname_from_module("get_plugin_logger", module)
    assert x == "mkdocs.plugins.get_plugin_logger"


def test_get_fullname_config():
    from astdoc.node import get_fullname_from_module

    module = "astdoc.config"
    x = get_fullname_from_module("Config", module)
    assert x == "mkdocs.config.base.Config"
    x = get_fullname_from_module("config_options", module)
    assert x == "mkdocs.config.config_options"
    x = get_fullname_from_module("config_options.Type", module)
    assert x == "mkdocs.config.config_options.Type"


def test_get_fullname_nested():
    from astdoc.node import get_fullname_from_module

    assert get_fullname_from_module("astdoc.doc.Item.name") == "astdoc.doc.Item.name"
    assert not get_fullname_from_module("astdoc.doc.Item.astdoc")


def test_get_fullname_method():
    from astdoc.node import get_fullname_from_module

    assert get_fullname_from_module("astdoc.doc.Item.clone") == "astdoc.doc.Item.clone"
    assert (
        get_fullname_from_module("Item.clone", "astdoc.doc") == "astdoc.doc.Item.clone"
    )
    assert get_fullname_from_module("Item", "astdoc.parser") == "astdoc.doc.Item"
    assert (
        get_fullname_from_module("Item.clone", "astdoc.parser")
        == "astdoc.doc.Item.clone"
    )
