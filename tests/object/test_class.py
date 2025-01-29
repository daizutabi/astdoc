import ast
import inspect

import pytest


def test_create_class_nested():
    from astdoc.object import Class, create_class

    src = """
    class A:
        class B:
            class C:
                pass
    """
    node = ast.parse(inspect.cleandoc(src)).body[0]
    assert isinstance(node, ast.ClassDef)
    cls = create_class(node, "test_create_class_nested", None)
    assert len(cls.children) == 1
    cls = cls.children["B"]
    assert isinstance(cls, Class)
    assert len(cls.children) == 1
    cls = cls.children["C"]
    assert isinstance(cls, Class)


def test_create_class(get):
    from astdoc.object import Class, Function, Property, create_class

    node = get("ExampleClass")
    assert isinstance(node, ast.ClassDef)
    cls = create_class(node, "test_create_class", None)
    assert isinstance(cls, Class)
    assert cls.name == "ExampleClass"
    assert len(cls.raises) == 0
    for x in ["_private"]:
        assert isinstance(cls.get(x), Function)
    for x in ["readonly_property", "readwrite_property"]:
        assert isinstance(cls.get(x), Property)


def test_create_class_cache(get):
    from astdoc.object import create_class

    node = get("ExampleClass")
    assert isinstance(node, ast.ClassDef)
    cls = create_class(node, "test_create_class", None)
    cls2 = create_class(node, "test_create_class", None)
    assert cls is cls2


def test_inherit():
    from astdoc.object import Class, Function, create_module

    module = create_module("astdoc.object")
    assert module
    cls = module.get("Class")
    assert isinstance(cls, Class)
    func = cls.get("__repr__")
    assert isinstance(func, Function)
    assert func.qualname == "Object.__repr__"


def test_class_parameters():
    from astdoc.object import Class, create_module
    from astdoc.utils import find_item_by_name

    module = create_module("examples._styles.google")
    assert module
    cls = module.get("ExampleClass")
    assert isinstance(cls, Class)
    assert len(cls.parameters) == 3
    module = create_module("astdoc.object")
    assert module
    cls = module.get("Class")
    assert isinstance(cls, Class)
    assert find_item_by_name(cls.parameters, "name")
    assert find_item_by_name(cls.parameters, "node")
    assert find_item_by_name(cls.parameters, "module")
    assert find_item_by_name(cls.parameters, "parent")


def test_inherit_base_classes_parser():
    from astdoc.object import Class, create_module

    module = create_module("astdoc.doc")
    assert module
    cls = module.get("Section")
    assert isinstance(cls, Class)
    assert cls.get("clone")


def test_inherit_base_classes_ast():
    from astdoc.object import Class, create_module

    module = create_module("astdoc.ast")
    assert module
    cls = module.get("Parameter")
    assert isinstance(cls, Class)
    assert cls.get("name")
    assert cls.get("type")
    assert cls.get("default")


def test_iter_dataclass_parameters():
    from astdoc.object import Class, create_module

    module = create_module("astdoc.ast")
    assert module
    cls = module.get("Parameter")
    assert isinstance(cls, Class)
    p = cls.parameters
    assert p[0].name == "name"
    assert p[1].name == "type"
    assert p[2].name == "default"
    assert p[3].name == "kind"


def test_iter_attributes_from_function():
    from astdoc.object import Class, create_module

    module = create_module("examples._styles.google")
    assert module
    cls = module.get("ExampleClass")
    assert isinstance(cls, Class)
    for k in range(1, 6):
        assert f"attr{k}" in cls.children


def test_type():
    from astdoc.object import Attribute, Class, Property, create_module

    module = create_module("examples._styles.google")
    assert module
    cls = module.get("ExampleClass")
    assert isinstance(cls, Class)
    x = cls.get("attr4")
    assert isinstance(x, Attribute)
    assert x.type is None
    assert x.doc.type == "list(str)"
    x = cls.get("readonly_property")
    assert isinstance(x, Property)
    assert x.type is None
    assert x.doc.type == "str"


def test_merge_init_doc():
    from astdoc.object import Class, create_module

    module = create_module("examples._styles.google")
    assert module
    cls = module.get("ExampleClass")
    assert isinstance(cls, Class)
    assert cls.doc.text
    assert len(cls.doc.sections) == 2


def test_children_order():
    from astdoc.object import Class, get_object

    cls = get_object("astdoc.node.Import")
    assert isinstance(cls, Class)
    names = list(cls.children.keys())
    assert names[0] == "name"
    assert names[1] == "node"
    assert names[-1] == "fullname"


@pytest.mark.parametrize(
    "name",
    [
        "name",
        "value",
        "POSITIONAL_ONLY",
        "POSITIONAL_OR_KEYWORD",
        "VAR_POSITIONAL",
        "KEYWORD_ONLY",
        "VAR_KEYWORD",
    ],
)
def test_enum(name):
    from astdoc.object import Class, get_object

    cls = get_object("inspect._ParameterKind")
    assert isinstance(cls, Class)
    assert name in [name for name, _ in cls.get_children()]
