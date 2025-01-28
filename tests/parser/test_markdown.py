import ast

import pytest


@pytest.mark.parametrize(
    "text",
    [
        "`abc`",
        "`abc[abc]`",
        "```abc```",
        "`` `abc` ``",
    ],
)
def test_code_pattern_match(text):
    from astdoc.parser import CODE_PATTERN

    m = CODE_PATTERN.match(text)
    assert m
    assert m.group() == text


def test_get_markdown_name_noreplace():
    from astdoc.parser import get_markdown_name

    x = get_markdown_name("abc")
    assert x == "[abc][__astdoc__.abc]"
    x = get_markdown_name("a_._b.c")
    assert r"[a\_][__astdoc__.a_]." in x
    assert r".[\_b][__astdoc__.a_._b]." in x
    assert ".[c][__astdoc__.a_._b.c]" in x


def test_get_markdown_name():
    from astdoc.node import get_fullname_from_module
    from astdoc.parser import get_markdown_name

    def replace(name: str) -> str | None:  # type: ignore
        return get_fullname_from_module(name, "astdoc.object")

    x = get_markdown_name("Object", replace)
    assert x == "[Object][__astdoc__.astdoc.object.Object]"
    x = get_markdown_name("Object.__repr__", replace)
    assert r".[\_\_repr\_\_][__astdoc__.astdoc.object.Object.__repr__]" in x

    def replace(name: str) -> str | None:  # type: ignore
        return get_fullname_from_module(name, "astdoc.plugin")

    x = get_markdown_name("MkDocsPage", replace)
    assert x == "[MkDocsPage][__astdoc__.mkdocs.structure.pages.Page]"

    def replace(name: str) -> str | None:
        return get_fullname_from_module(name, "mkdocs.plugins")

    x = get_markdown_name("jinja2.Template", replace)
    assert "[jinja2][__astdoc__.jinja2]." in x
    assert "[Template][__astdoc__.jinja2.environment.Template]" in x

    assert get_markdown_name("str", replace) == "str"
    assert get_markdown_name("None", replace) == "None"
    assert get_markdown_name("_abc", replace) == "\\_abc"


def test_get_markdown_str():
    from astdoc.node import get_fullname_from_module
    from astdoc.parser import get_markdown_str

    def replace(name: str) -> str | None:
        return get_fullname_from_module(name, "astdoc.object")

    type_string = "1 Object or Class."
    x = get_markdown_str(type_string, replace)
    assert "1 [Object][__astdoc__.astdoc.object.Object] " in x
    assert "or [Class][__astdoc__.astdoc.object.Class]." in x


def test_get_markdown_expr():
    from astdoc.node import get_fullname_from_module
    from astdoc.parser import get_markdown_expr

    def replace(name: str) -> str | None:
        return get_fullname_from_module(name, "astdoc.markdown")

    expr = ast.parse("re.Match[finditer](sub)").body[0].value  # type: ignore
    assert isinstance(expr, ast.expr)
    x = get_markdown_expr(expr, replace)
    assert x.startswith("[re][__astdoc__.re].[Match][__astdoc__.re.Match]")
    assert "[[finditer][__astdoc__.astdoc.markdown.finditer]]" in x
    assert x.endswith("([sub][__astdoc__.astdoc.markdown.sub])")


def test_get_markdown_expr_constant():
    from astdoc.node import get_fullname_from_module
    from astdoc.parser import get_markdown_expr

    def replace(name: str) -> str | None:
        return get_fullname_from_module(name, "astdoc.markdown")

    expr = ast.Constant("re.Match")
    assert isinstance(expr, ast.expr)
    x = get_markdown_expr(expr, replace)
    assert x == "[re][__astdoc__.re].[Match][__astdoc__.re.Match]"

    expr = ast.Constant(123)
    assert isinstance(expr, ast.expr)
    x = get_markdown_expr(expr, replace)
    assert x == "123"


def test_get_markdown_text_module_objects():
    from astdoc.node import get_fullname_from_module
    from astdoc.parser import get_markdown_text

    def replace(name: str) -> str | None:
        return get_fullname_from_module(name, "astdoc.object")

    x = get_markdown_text("Class", replace)
    assert x == "Class"
    x = get_markdown_text("a `Class` b", replace)
    assert x == "a [`Class`][__astdoc__.astdoc.object.Class] b"
    x = get_markdown_text("a `Class ` b", replace)
    assert x == "a `Class ` b"
    x = get_markdown_text("a `invalid` b", replace)
    assert x == "a `invalid` b"
    x = get_markdown_text("a `` `Class` `` b", replace)
    assert x == "a `` `Class` `` b"
    m = "a \n```\n`Class`\n```\n b"
    assert get_markdown_text(m, replace) == m


def test_get_markdown_text_module_plugins():
    from astdoc.node import get_fullname_from_module
    from astdoc.parser import get_markdown_text

    def replace(name: str) -> str | None:
        return get_fullname_from_module(name, "astdoc.plugin")

    x = get_markdown_text("a `astdocPlugin` b", replace)
    assert x == "a [`astdocPlugin`][__astdoc__.astdoc.plugin.astdocPlugin] b"
    x = get_markdown_text("a `BasePlugin` b", replace)
    assert x == "a [`BasePlugin`][__astdoc__.mkdocs.plugins.BasePlugin] b"
    x = get_markdown_text("a `MkDocsConfig` b", replace)
    assert x == "a [`MkDocsConfig`][__astdoc__.mkdocs.config.defaults.MkDocsConfig] b"
    x = get_markdown_text("a [b] c", replace)
    assert x == "a [b] c"


def test_get_markdown_type_none():
    from astdoc.parser import get_markdown_type

    x = get_markdown_type(None, None)
    assert x == ""
    from astdoc.parser import get_markdown_type
