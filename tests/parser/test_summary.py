def test_classes_fom_module():
    from astdoc.parser import create_classes_from_module

    name = "astdoc.node"
    section = create_classes_from_module(name)
    assert section
    assert section.name == "Classes"
    name = "[Node][__astdoc__.astdoc.node.Node]"
    assert section.items[0].name == name


def test_classes_from_module_alias():
    from astdoc.parser import create_classes_from_module

    name = "examples._styles"
    section = create_classes_from_module(name)
    assert section
    assert section.name == "Classes"
    name = "[ExampleClassGoogle][__astdoc__.examples._styles.ExampleClassGoogle]"
    assert section.items[0].name == name
    assert section.items[0].text.startswith("The summary")


def test_functions_from_module():
    from astdoc.parser import create_functions_from_module

    name = "astdoc.node"
    section = create_functions_from_module(name)
    assert section
    assert section.name == "Functions"
    names = [i.name for i in section.items]
    name = "[iter\\_child\\_nodes][__astdoc__.astdoc.node.iter_child_nodes]"
    assert any(name in n for n in names)


def test_methods_from_class():
    from astdoc.parser import create_methods_from_class

    section = create_methods_from_class("astdocPlugin", "astdoc.plugin")
    assert section
    assert section.name == "Methods"
    names = [i.name for i in section.items]
    name = "[on\\_nav][__astdoc__.astdoc.plugin.astdocPlugin.on_nav]"
    assert any(name in n for n in names)


def test_methods_from_class_property():
    from astdoc.parser import create_methods_from_class

    assert not create_methods_from_class("Object", "astdoc.object")


def test_modules_from_module_file():
    from astdoc.parser import create_modules_from_module_file

    section = create_modules_from_module_file("examples.sub")
    assert section
    assert section.name == "Modules"
    names = [i.name for i in section.items]
    assert len(names) == 3
    name = "[examples.sub.subsub][__astdoc__.examples.sub.subsub]"
    assert any(name in n for n in names)
    assert all("_pmod" not in n for n in names)


def test_modules_from_module_file_not_package():
    from astdoc.parser import create_modules_from_module_file

    section = create_modules_from_module_file("examples.mod_a")
    assert not section
