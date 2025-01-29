import ast
import inspect

import pytest

from astdoc.object import Class


def test_create_module():
    from astdoc.object import create_module

    module = create_module("examples._styles.google")
    assert module
    assert module.get("ExampleClass")


def test_create_function():
    from astdoc.object import Function, create_module
    from astdoc.utils import find_item_by_name

    module = create_module("examples._styles.google")
    assert module
    func = module.get("module_level_function")
    assert isinstance(func, Function)
    assert func.name == "module_level_function"
    assert func.qualname == "module_level_function"
    assert len(func.parameters) == 4
    assert find_item_by_name(func.parameters, "param1")
    assert find_item_by_name(func.parameters, "param2")
    assert find_item_by_name(func.parameters, "args")
    assert find_item_by_name(func.parameters, "kwargs")
    assert len(func.raises) == 1


def test_iter_objects():
    from astdoc.object import create_module, iter_objects

    src = """'''test module.'''
    m: str
    n = 1
    '''int: attribute n.'''
    class A(D):
        '''class.

        Attributes:
            a: attribute a.
        '''
        a: int
        def f(x: int, y: str) -> list[str]:
            '''function.'''
            class B(E,F.G):
                c: list
            raise ValueError
    """
    src = inspect.cleandoc(src)
    assert src
    node = ast.parse(src)
    module = create_module("test_iter_objects", node)
    assert module
    objs = iter_objects(module)
    assert next(objs).name == "m"
    assert next(objs).name == "n"
    assert next(objs).name == "A"
    assert next(objs).name == "a"
    assert next(objs).name == "f"
    assert next(objs).name == "B"
    assert next(objs).name == "c"


def test_iter_objects_none():
    from astdoc.object import iter_objects

    assert not list(iter_objects(None))  # type: ignore


def test_get_object_kind_package():
    from astdoc.object import create_module, get_object_kind

    module = create_module("astdoc")
    assert module
    assert get_object_kind(module) == "package"


@pytest.fixture
def astdoc_objects():
    from astdoc.object import create_module

    module = create_module("astdoc.object")
    assert module
    return module


def test_get_object_kind_module(astdoc_objects):
    from astdoc.object import get_object_kind

    assert get_object_kind(astdoc_objects) == "module"
    assert astdoc_objects.kind == "module"


def test_get_object_kind_dataclass(astdoc_objects):
    from astdoc.object import get_object_kind

    cls = astdoc_objects.get("Object")
    assert get_object_kind(cls) == "dataclass"
    assert cls.kind == "dataclass"


def test_get_object_kind_function(astdoc_objects):
    from astdoc.object import get_object_kind

    func = astdoc_objects.get("create_function")
    assert get_object_kind(func) == "function"
    assert func.kind == "function"


def test_get_object_kind_method(astdoc_objects):
    from astdoc.object import get_object_kind

    cls = astdoc_objects.get("Object")
    method = cls.get("__post_init__")
    assert get_object_kind(method) == "method"
    assert method.kind == "method"


def test_get_object_kind_attribute(astdoc_objects):
    from astdoc.object import get_object_kind

    cls = astdoc_objects.get("Object")
    attribute = cls.get("node")
    assert get_object_kind(attribute) == "attribute"
    assert attribute.kind == "attribute"


def test_get_source_module(astdoc_objects):
    from astdoc.object import get_source

    s = get_source(astdoc_objects)
    assert s
    assert "def create_module(" in s


def test_get_source_function(astdoc_objects):
    from astdoc.object import get_source

    func = astdoc_objects.get("create_module")
    s = get_source(func)
    assert s
    assert s.startswith("def create_module")


def test_get_source_examples():
    from astdoc.object import create_module, get_source

    module = create_module("examples._styles.google")
    assert module
    s = get_source(module)
    assert s
    assert s.startswith('"""Example')
    assert s.endswith("attr2: int\n")
    cls = module.get("ExampleClass")
    assert cls
    s = get_source(cls)
    assert s
    assert s.startswith("class ExampleClass")
    assert s.endswith("pass")


@pytest.fixture
def parser():
    from astdoc.object import create_module

    module = create_module("astdoc.object")
    assert module
    cls = module.get("Function")
    assert isinstance(cls, Class)
    return cls


@pytest.mark.parametrize("name", ["replace_from_module", "replace_from_object"])
def test_is_child(parser: Class, name):
    from astdoc.object import is_child

    for name_, obj in parser.children.items():
        if name_ == name:
            assert is_child(obj, parser)


def test_is_child_true_parent_none():
    from astdoc.object import get_object, is_child

    obj = get_object("ast.parse")
    assert obj
    assert is_child(obj, None)


def test_is_child_true_obj_module():
    from astdoc.object import get_object, is_child

    obj = get_object("ast")
    assert obj
    assert is_child(obj, None)


def test_is_child_true_parent_module():
    from astdoc.object import get_object, is_child

    obj = get_object("ast")
    module = get_object("inspect")
    assert obj
    assert module
    assert is_child(obj, module)


@pytest.mark.parametrize("attr", ["", ".example_method"])
@pytest.mark.parametrize(
    ("name", "module"),
    [
        ("examples._styles.ExampleClassGoogle", None),
        ("ExampleClassGoogle", "examples._styles"),
    ],
)
def test_get_object_class(attr, name, module):
    from astdoc.object import get_object

    x = get_object(f"{name}{attr}", module)
    assert x
    assert x.module == "examples._styles.google"
    qualname = f"ExampleClass{attr}"
    assert x.qualname == qualname
    assert x.name == qualname.split(".")[-1]


def test_get_object_cache():
    from astdoc.object import create_module, get_object

    assert create_module("astdoc.object") is get_object("astdoc.object")


def test_get_object_cache_():
    from astdoc.object import Class, Function, get_object

    c = get_object("astdoc.object.Object")
    f = get_object("astdoc.object.Module.__post_init__")
    assert isinstance(c, Class)
    assert c.module == "astdoc.object"
    assert isinstance(f, Function)
    assert f.module == "astdoc.object"
    c2 = get_object("astdoc.object.Object")
    f2 = get_object("astdoc.object.Module.__post_init__")
    assert c is c2
    assert f is f2


def test_get_fullname_from_object():
    from astdoc.object import get_fullname_from_object, get_object

    x = get_object("astdoc.object")
    assert x
    r = get_fullname_from_object("Object", x)
    assert r == "astdoc.object.Object"
    x = get_object(r)
    assert x
    r = get_fullname_from_object("__repr__", x)
    assert r == "astdoc.object.Object.__repr__"
    x = get_object(r)
    assert x
    r = get_fullname_from_object("__post_init__", x)
    assert r == "astdoc.object.Object.__post_init__"
    x = get_object(r)
    assert x
    r = get_fullname_from_object("Object", x)
    assert r == "astdoc.object.Object"


def test_get_fullname_from_object_method():
    from astdoc.object import get_fullname_from_object, get_object

    x = get_object("astdoc.doc.merge")
    assert x
    r = get_fullname_from_object("Item", x)
    assert r == "astdoc.doc.Item"
    r = get_fullname_from_object("Item.clone", x)
    assert r == "astdoc.doc.Item.clone"


def test_get_object_asname():
    from astdoc.object import get_object

    name = "examples._styles.ExampleClassGoogle.example_method"
    obj = get_object(name)
    assert obj
    assert obj.name == "example_method"
    assert obj.module == "examples._styles.google"
    assert obj.fullname == "examples._styles.google.ExampleClass.example_method"


def test_get_object_export():
    from astdoc.object import get_object

    name = "jinja2.Environment.compile"
    obj = get_object(name)
    assert obj
    assert obj.name == "compile"
    assert obj.module == "jinja2.environment"
    assert obj.fullname == "jinja2.environment.Environment.compile"


def test_object_repr():
    from astdoc.object import get_object

    name = "astdoc"
    obj = get_object(name)
    assert obj
    assert repr(obj) == "Module('astdoc')"
