import ast
import datetime
import importlib
import time
from collections import namedtuple
from pathlib import Path

import pytest


def test_cache():
    from astdoc.utils import cache, cache_clear, cached_objects

    @cache
    def f():
        return datetime.datetime.now()  # noqa: DTZ005

    c = cache({})

    assert f in cached_objects
    x = f()
    time.sleep(0.1)
    y = f()
    assert x == y
    assert f.cache_info().currsize == 1
    cache_clear()
    assert f.cache_info().currsize == 0
    time.sleep(0.1)
    z = f()
    assert x != z
    assert f.cache_info().currsize == 1
    c[1] = 1
    cache_clear()
    assert not c


@pytest.mark.parametrize(
    "name",
    ["collections", "examples", "namespace.sub"],
)
def test_get_module_path(name):
    from astdoc.utils import get_module_path

    assert get_module_path(name)


@pytest.mark.parametrize("name", ["sys", "a.b", "namespace"])
def test_get_module_path_none(name):
    from astdoc.utils import get_module_path

    assert get_module_path(name) is None


def test_get_module_name():
    from astdoc.utils import get_module_name

    name = "_collections_abc"
    abc = importlib.import_module(name)
    assert abc.__name__ == "collections.abc"
    assert get_module_name(name) == "collections.abc"


def test_is_module():
    from astdoc.utils import _is_module, get_module_path

    path = get_module_path("astdoc.object")
    assert path
    assert not _is_module(path, r"^astdoc\..+")


@pytest.mark.parametrize(
    ("name", "b"),
    [
        ("astdoc", True),
        ("astdoc.object", False),
        ("sys", False),
        ("a.b", False),
        ("examples", True),
        ("namespace", True),
    ],
)
def test_is_package(name, b):
    from astdoc.utils import is_package

    assert is_package(name) is b


@pytest.mark.parametrize("name", ["astdoc"])
def test_iter_submodule_names(name):
    from astdoc.utils import iter_submodule_names

    names = list(iter_submodule_names(name))
    assert names
    assert all(n.startswith(name) for n in names)


def test_iter_submodule_names_namespace():
    from astdoc.utils import iter_submodule_names

    names = list(iter_submodule_names("namespace"))
    assert names == ["namespace.sub"]


def test_iter_submodule_names_none():
    from astdoc.utils import iter_submodule_names

    assert not list(iter_submodule_names("sys"))


def test_find_submodule_names():
    from astdoc.utils import find_submodule_names

    names = find_submodule_names("astdoc", lambda x: "node" not in x)
    assert "astdoc.node" not in names
    assert "astdoc.ast" in names


def test_get_module_node():
    from astdoc.utils import get_module_node

    node1 = get_module_node("astdoc")
    assert node1
    node2 = get_module_node("astdoc")
    assert node1 is node2


def test_get_module_node_none():
    from astdoc.utils import get_module_node

    assert not get_module_node("sys")


def test_find_item_by_name():
    from astdoc.utils import find_item_by_name

    A = namedtuple("A", ["name", "value"])  # noqa: PYI024
    x = [A("a", 1), A("a", 2), A("b", 3), A("c", 4)]
    a = find_item_by_name(x, "a")
    assert a
    assert a.value == 1
    assert not find_item_by_name(x, "d")


def test_find_item_by_name_list():
    from astdoc.utils import find_item_by_name

    A = namedtuple("A", ["name", "value"])  # noqa: PYI024
    x = [A("a", 1), A("a", 2), A("b", 3), A("c", 4)]
    a = find_item_by_name(x, ["x", "a"])
    assert a
    assert a.name == "a"


def test_find_item_by_name_none():
    from astdoc.utils import find_item_by_name

    A = namedtuple("A", ["name", "value"])  # noqa: PYI024
    x = [A("a", 1), A("a", 2), A("b", 3), A("c", 4)]
    assert find_item_by_name(x, ["d", "e"]) is None


def test_find_item_by_kind():
    from astdoc.utils import find_item_by_kind

    A = namedtuple("A", ["kind", "value"])  # noqa: PYI024
    x = [A("a", 1), A("a", 2), A("b", 3), A("c", 4)]
    a = find_item_by_kind(x, "a")
    assert a
    assert a.value == 1
    assert not find_item_by_kind(x, "d")


def test_find_item_by_type():
    from astdoc.utils import find_item_by_type

    A = namedtuple("A", ["name", "value"])  # noqa: PYI024
    B = namedtuple("B", ["name", "value"])  # noqa: PYI024
    x = [A("a", 1), A("a", 2), B("b", 3), B("c", 4)]
    a = find_item_by_type(x, B)
    assert a
    assert a.value == 3
    assert not find_item_by_type(x, int)


def test_delete_item_by_name():
    from astdoc.utils import delete_item_by_name, find_item_by_name

    A = namedtuple("A", ["name", "value"])  # noqa: PYI024
    x = [A("a", 1), A("a", 2), A("b", 3), A("c", 4)]
    delete_item_by_name(x, "a")
    assert len(x) == 3
    a = find_item_by_name(x, "a")
    assert a
    assert a.value == 2
    x = [A("a", 1), A("a", 2), A("b", 3), A("c", 4)]
    delete_item_by_name(x, "c")
    assert x == [A("a", 1), A("a", 2), A("b", 3)]


def test_merge_unique_names():
    from astdoc.utils import merge_unique_names

    A = namedtuple("A", ["name", "value"])  # noqa: PYI024
    x = [A("a", 1), A("a", 2), A("b", 3), A("c", 4)]
    y = [A("b", 1), A("a", 2), A("d", 3), A("e", 4)]
    assert merge_unique_names(x, y) == ["a", "a", "b", "c", "d", "e"]


def test_iter_identifiers():
    from astdoc.utils import iter_identifiers

    x = "a, b, c"
    y = list(iter_identifiers(x))
    assert y[0] == ("a", True)
    assert y[3] == ("b", True)
    assert y[6] == ("c", True)
    x = "a.b[c], def(xyz)"
    y = list(iter_identifiers(x))
    assert y[0] == ("a.b", True)
    assert y[2] == ("c", True)
    assert y[6] == ("def", True)
    assert y[8] == ("xyz", True)
    x = "abc'def'"
    y = list(iter_identifiers(x))
    assert y == [("abc", True), ("'def'", False)]
    x = "abc."
    y = list(iter_identifiers(x))
    assert y == [("abc", True), (".", False)]
    x = "1"
    assert next(iter_identifiers(x)) == ("1", False)
    x = "a1"
    assert next(iter_identifiers(x)) == ("a1", True)
    x = "a,b"
    assert list(iter_identifiers(x)) == [("a", True), (",", False), ("b", True)]
    x = "dict, Sequence, ndarray, 'Series', or pandas.DataFrame."
    x = list(iter_identifiers(x))
    assert ("dict", True) in x
    assert ("Sequence", True) in x
    assert ("'Series'", False) in x
    assert ("pandas.DataFrame", True) in x


def test_list_exported_names():
    from astdoc.utils import list_exported_names

    x = list_exported_names("examples._styles")
    assert "ExampleClassNumPy" in x
    assert "ExampleClassGoogle" in x


def test_get_object():
    from astdoc.utils import get_object_from_module

    name = "ExampleClass"
    module = "examples._styles.google"
    obj = get_object_from_module(name, module)
    assert obj.__name__ == name  # type: ignore
    assert obj.__module__ == module


def test_get_object_asname():
    from astdoc.utils import get_object_from_module

    name_ = "ExampleClassGoogle"
    module_ = "examples._styles"
    obj = get_object_from_module(name_, module_)
    assert obj.__name__ == "ExampleClass"  # type: ignore
    assert obj.__module__ == "examples._styles.google"


def test_get_base_classes():
    from astdoc.utils import get_base_classes

    x = get_base_classes("Class", "astdoc.object")
    assert x == [("Definition", "astdoc.object")]


def test_split_module_name_module():
    from astdoc.utils import split_module_name

    assert split_module_name("ast") == ("ast", None)


def test_split_module_name_submodule():
    from astdoc.utils import split_module_name

    assert split_module_name("astdoc.node") == ("astdoc.node", None)


def test_split_module_name_module_imported():
    from astdoc.utils import split_module_name

    assert split_module_name("astdoc.object.ast") == ("ast", "astdoc.object")


def test_split_module_name_class():
    from astdoc.utils import split_module_name

    assert split_module_name("ast.ClassDef") == ("ClassDef", "ast")


def test_split_module_name_asname():
    from astdoc.utils import split_module_name

    x = split_module_name("examples._styles.ExampleClassGoogle")
    assert x == ("ExampleClassGoogle", "examples._styles")


def test_split_module_name_none():
    from astdoc.utils import split_module_name

    assert not split_module_name("x.x")


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("namespace", None),
        ("namespace.sub", ("namespace.sub", None)),
        ("namespace.sub.func", ("func", "namespace.sub")),
        ("namespace.unknown", ("unknown", "namespace")),
        ("namespace.sub.unknown", ("unknown", "namespace.sub")),
    ],
)
def test_split_module_name_namespace(name, expected):
    from astdoc.utils import split_module_name

    assert split_module_name(name) == expected


@pytest.fixture(autouse=True)
def clear_cache():
    from astdoc.utils import cache_clear

    cache_clear()


def test_cache_function():
    from astdoc.utils import cache

    @cache
    def sample_function(x):
        return x * 2

    assert sample_function(5) == 10
    assert sample_function(5) == 10


def test_cache_clear():
    from astdoc.utils import cache, cache_clear

    @cache
    def sample_function(x):
        return x * 2

    sample_function(5)
    cache_clear()
    assert sample_function(5) == 10


def test_is_module_none():
    from astdoc.utils import _is_module

    assert _is_module(Path(__file__))
    assert not _is_module(Path("non_existent_path"))


def test_is_package_none():
    from astdoc.utils import is_package

    assert is_package("astdoc")
    assert not is_package("non_existent_module")


def test_get_object_from_module():
    from astdoc.utils import get_object_from_module

    assert get_object_from_module("Path", "pathlib") is not None
    assert get_object_from_module("NonExistent", "my_module") is None


def test_get_module_node_source():
    from astdoc.utils import get_module_node_source

    node, source = get_module_node_source("os")  # type: ignore
    assert isinstance(node, ast.Module)
    assert isinstance(source, str)

    assert get_module_node_source("non_existent_module") is None


def test_is_enum():
    from astdoc.utils import is_enum

    assert is_enum("_ParameterKind", "inspect")
