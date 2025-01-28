import pytest

from astdoc.doc import Doc


def test_node_object():
    from astdoc.node import Definition, get_node
    from astdoc.object import Class, get_object

    name = "jinja2.Template"
    obj = get_object(name)
    assert isinstance(obj, Class)
    assert obj.name == "Template"
    assert obj.module == "jinja2.environment"
    assert obj.fullname == "jinja2.environment.Template"

    node = get_node(name)
    assert isinstance(node, Definition)
    assert node.name == "Template"
    assert node.module == "jinja2.environment"

    assert node.node is obj.node


def test_parser_module():
    from astdoc.parser import Parser

    name = "astdoc.node"
    parser = Parser.create(name)
    assert parser
    assert parser.name == "astdoc.node"
    assert parser.module is None
    assert parser.obj.fullname == "astdoc.node"


def test_parser_class():
    from astdoc.parser import Parser

    name = "astdoc.node.Module"
    parser = Parser.create(name)
    assert parser
    assert parser.name == "Module"
    assert parser.module == "astdoc.node"
    assert parser.obj.fullname == "astdoc.node.Module"


def test_parser_class_alias():
    from astdoc.parser import Parser

    name = "jinja2.Template"
    parser = Parser.create(name)
    assert parser
    assert parser.name == "Template"
    assert parser.module == "jinja2"
    assert parser.obj.fullname == "jinja2.environment.Template"


def test_parser_function():
    from astdoc.parser import Parser

    name = "astdoc.node.get_node"
    parser = Parser.create(name)
    assert parser
    assert parser.name == "get_node"
    assert parser.module == "astdoc.node"
    assert parser.obj.fullname == "astdoc.node.get_node"


def test_parser_method():
    from astdoc.parser import Parser

    name = "astdoc.parser.Parser.create"
    parser = Parser.create(name)
    assert parser
    assert parser.name == "Parser.create"
    assert parser.module == "astdoc.parser"
    assert parser.obj.fullname == "astdoc.parser.Parser.create"


def test_parser_method_alias():
    from astdoc.parser import Parser

    name = "jinja2.Template.render"
    parser = Parser.create(name)
    assert parser
    assert parser.name == "Template.render"
    assert parser.module == "jinja2"
    assert parser.obj.fullname == "jinja2.environment.Template.render"


def test_parser_invalid_package():
    from astdoc.parser import Parser

    name = "invalid"
    parser = Parser.create(name)
    assert parser is None


def test_parser_invalid_module():
    from astdoc.parser import Parser

    name = "astdoc.invalid"
    parser = Parser.create(name)
    assert parser is None


def test_parser_repr_module():
    from astdoc.parser import Parser

    name = "astdoc.node"
    parser = Parser.create(name)
    assert repr(parser) == "Parser('astdoc.node', None)"


def test_parser_repr_object():
    from astdoc.parser import Parser

    name = "astdoc.node.Node"
    parser = Parser.create(name)
    assert repr(parser) == "Parser('Node', 'astdoc.node')"


def test_parse_name_set_module():
    from astdoc.parser import Parser

    name = "astdoc.ast"
    parser = Parser.create(name)
    assert parser
    name_set = parser.parse_name_set()
    assert name_set.kind == "module"
    assert name_set.name == "astdoc.ast"
    assert name_set.parent is None
    assert name_set.module is None
    assert name_set.fullname == "astdoc.ast"
    assert name_set.id == "astdoc.ast"
    assert name_set.obj_id == "astdoc.ast"
    assert name_set.parent_id is None


def test_parse_name_set_function():
    from astdoc.parser import Parser

    name = "astdoc.ast.get_assign_name"
    parser = Parser.create(name)
    assert parser
    name_set = parser.parse_name_set()
    assert name_set.kind == ""
    assert name_set.name == "get\\_assign\\_name"
    assert name_set.parent is None
    assert name_set.module == "astdoc.ast"
    assert name_set.fullname == "astdoc.ast.get\\_assign\\_name"
    assert name_set.id == "astdoc.ast.get_assign_name"
    assert name_set.obj_id == "astdoc.ast.get_assign_name"
    assert name_set.parent_id is None


def test_parse_name_set_staticmethod():
    from astdoc.parser import Parser

    name = "astdoc.parser.Parser.create"
    parser = Parser.create(name)
    assert parser
    name_set = parser.parse_name_set()
    assert name_set.kind == "classmethod"
    assert name_set.name == "create"
    assert name_set.parent == "Parser"
    assert name_set.module == "astdoc.parser"
    assert name_set.fullname == "astdoc.parser.Parser.create"
    assert name_set.id == "astdoc.parser.Parser.create"
    assert name_set.obj_id == "astdoc.parser.Parser.create"
    assert name_set.parent_id == "astdoc.parser.Parser"


def test_parse_name_set_export():
    from astdoc.parser import Parser

    name = "jinja2.Template.render"
    parser = Parser.create(name)
    assert parser
    name_set = parser.parse_name_set()
    assert name_set.id == "jinja2.Template.render"
    assert name_set.obj_id == "jinja2.environment.Template.render"
    assert name_set.fullname == "jinja2.Template.render"


def test_parse_name_set_alias():
    from astdoc.parser import Parser

    name = "examples._styles.ExampleClassGoogle"
    parser = Parser.create(name)
    assert parser
    name = parser.parse_name_set()
    assert name.id == "examples._styles.ExampleClassGoogle"
    assert name.obj_id == "examples._styles.google.ExampleClass"
    assert name.fullname == "examples.\\_styles.ExampleClassGoogle"


def test_parse_signature():
    from astdoc.parser import Parser

    name = "astdoc.ast._iter_parameters"
    parser = Parser.create(name)
    assert parser
    signature = parser.parse_signature()
    assert signature[0] == ("(", "paren")
    assert signature[1] == ("node", "arg")
    assert signature[2] == (": ", "colon")
    assert signature[3][0].startswith("[FunctionDef][__astdoc__.ast.FunctionDef] | [")
    assert signature[3][0].endswith("][__astdoc__.ast.AsyncFunctionDef]")
    assert signature[3][1] == "ann"
    assert signature[4] == (")", "paren")
    assert signature[5] == (" → ", "arrow")
    assert signature[6][0].startswith("[Iterator][__astdoc__.collections.abc.Iterator][")
    assert signature[6][1] == "return"


@pytest.fixture
def doc_func():
    from astdoc.parser import Parser

    name = "examples._usage.func"
    parser = Parser.create(name)
    assert parser
    return parser.parse_doc()


def test_parse_doc_function_text(doc_func: Doc):
    assert doc_func.text == "Docstring [`D`][__astdoc__.astdoc.node.Definition]."


def test_parse_doc_function_args(doc_func: Doc):
    assert doc_func.sections[0].name == "Parameters"
    items = doc_func.sections[0].items
    assert items[0].name == "a"
    assert items[0].type == "[Object][__astdoc__.astdoc.object.Object]"
    assert items[0].text == "A."
    assert items[1].name == "b"
    assert items[1].text.startswith("B [`I`][__astdoc__.astdoc.doc.Item]")
    assert items[1].text.endswith(" [`Object`][__astdoc__.astdoc.object.Object].")


def test_parse_doc_function_returns(doc_func: Doc):
    assert doc_func.sections[1].name == "Returns"
    items = doc_func.sections[1].items
    assert items[0].name == ""
    assert items[0].type == "[I][__astdoc__.astdoc.doc.Item]"
    assert items[0].text == "C."


@pytest.fixture
def doc_class():
    from astdoc.parser import Parser

    name = "examples._usage.A"
    parser = Parser.create(name)
    assert parser
    return parser.parse_doc()


def test_parse_doc_class_text(doc_class: Doc):
    assert doc_class.text == "Docstring [`I`][__astdoc__.astdoc.doc.Item]."


def test_parse_doc_class_attrs(doc_class: Doc):
    assert doc_class.sections[0].name == "Attributes"
    items = doc_class.sections[0].items
    assert items[0].name == "x"
    assert items[0].type == "[D][__astdoc__.astdoc.node.Definition]"
    assert items[0].text == "Attribute [`D`][__astdoc__.astdoc.node.Definition]."


def test_parse_bases():
    from astdoc.parser import Parser

    name = "astdoc.plugin.astdocPlugin"
    parser = Parser.create(name)
    assert parser
    bases = parser.parse_bases()
    assert len(bases) == 1
    base = bases[0]
    assert base.startswith("[BasePlugin][__astdoc__.mkdocs.plugins.BasePlugin]")
    assert base.endswith("[[astdocConfig][__astdoc__.astdoc.config.astdocConfig]]")


def test_parse_bases_empty():
    from astdoc.parser import Parser

    name = "astdoc.plugin"
    parser = Parser.create(name)
    assert parser
    assert parser.parse_bases() == []


def test_parse_signature_empty():
    from astdoc.parser import Parser

    name = "astdoc.plugin"
    parser = Parser.create(name)
    assert parser
    assert parser.parse_signature() == []


def test_parsr_doc_summary_modules():
    from astdoc.parser import Parser

    name = "examples"
    parser = Parser.create(name)
    assert parser
    doc = parser.parse_doc()
    assert len(doc.sections) == 3
    assert doc.sections[0].name == "Classes"
    assert doc.sections[0].items[0].name == "[ClassA][__astdoc__.examples.ClassA]"
    assert doc.sections[1].name == "Functions"
    assert doc.sections[1].items[0].name == "[func\\_a][__astdoc__.examples.func_a]"
    assert doc.sections[2].name == "Modules"
    assert doc.sections[2].items[0].name == "[mod\\_a][__astdoc__.examples.mod_a]"


def test_parsr_doc_summary_classes():
    from astdoc.parser import Parser
    from astdoc.utils import find_item_by_name

    name = "examples._styles"
    parser = Parser.create(name)
    assert parser
    doc = parser.parse_doc()
    section = find_item_by_name(doc.sections, "Classes")
    assert section
    x = "[ExampleClassGoogle][__astdoc__.examples._styles.ExampleClassGoogle]"
    assert section.items[0].name == x
    x = "[ExampleClassNumPy][__astdoc__.examples._styles.ExampleClassNumPy]"
    assert section.items[1].name == x


def test_parsr_doc_summary_functions():
    from astdoc.parser import Parser
    from astdoc.utils import find_item_by_name

    name = "examples._styles.google"
    parser = Parser.create(name)
    assert parser
    doc = parser.parse_doc()
    section = find_item_by_name(doc.sections, "Functions")
    assert section
    assert len(section.items) == 4


def test_parsr_doc_summary_methods():
    from astdoc.parser import Parser
    from astdoc.utils import find_item_by_name

    name = "astdoc.doc.Item"
    parser = Parser.create(name)
    assert parser
    doc = parser.parse_doc()
    section = find_item_by_name(doc.sections, "Methods")
    assert section
    assert len(section.items) == 1
    x = "[clone][__astdoc__.astdoc.doc.Item.clone]"
    assert section.items[0].name == x
