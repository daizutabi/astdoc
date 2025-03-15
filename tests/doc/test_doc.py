import inspect


def test_normalize_code_block_indentation():
    from astdoc.doc import iter_sections, normalize_code_block_indentation
    from astdoc.markdown import convert_code_block

    text = "a\n\n    >>> b\n\nc\n\n    >>> d\n    1\n\ne"
    s = next(iter_sections(convert_code_block(text), "google"))
    t = normalize_code_block_indentation(s.text)
    assert "a\n\n```{.python" in t
    assert "input}\nb\n```\n\nc" in t
    assert "\nc\n\n```{.python" in t
    assert "input}\nd\n```\n\n```{.text" in t
    assert "output}\n1\n```\n\ne" in t


def test_create_doc():
    from astdoc.doc import create_doc

    doc = create_doc("")
    assert not doc.type
    assert not doc.text
    assert not doc.sections
    doc = create_doc("a:\n    b\n")
    assert not doc.type
    assert not doc.text
    assert doc.sections


def test_create_doc_doctest():
    from astdoc.doc import create_doc

    text = "a\n\n    >>> b\n\nc\n\n    >>> d\n    1\n\ne"
    t = create_doc(text).text
    assert "a\n\n```{.python" in t
    assert "input}\nb\n```\n\nc" in t
    assert "\nc\n\n```{.python" in t
    assert "input}\nd\n```\n\n```{.text" in t
    assert "output}\n1\n```\n\ne" in t


def test_create_doc_doctest_section():
    from astdoc.doc import create_doc

    text = "a\n\nExamples:\n    >>> b\n"
    doc = create_doc(text)
    t = doc.sections[0].text
    assert t.startswith("```{.python")
    assert t.endswith("input}\nb\n```")


def test_merge_sections():
    from astdoc.doc import create_doc, merge_sections

    doc = create_doc("a:\n    x\n\na:\n    y\n\nb:\n    z\n")
    s = doc.sections
    x = merge_sections(s[0], s[1])
    assert x.text == "x\n\ny"


def test_iter_merged_sections():
    from astdoc.doc import create_doc, iter_merged_sections

    doc = create_doc("a:\n    x\n\nb:\n    y\n\na:\n    z\n")
    s = doc.sections
    x = list(iter_merged_sections(s[0:2], [s[2]]))
    assert len(x) == 2


def test_is_empty():
    from astdoc.doc import create_doc, is_empty

    doc = create_doc("")
    assert is_empty(doc)
    doc = create_doc("a")
    assert not is_empty(doc)
    doc = create_doc("a:\n    b\n")
    assert not is_empty(doc)
    doc = create_doc("Args:\n    b: c\n")
    assert not is_empty(doc)
    doc = create_doc("Args:\n    b\n")
    assert is_empty(doc)
    doc.sections[0].items[0].text = ""
    assert is_empty(doc)


def test_iter_items_without_name():
    from astdoc.doc import iter_items_without_name

    text = "int: The return value."
    item = next(iter_items_without_name(text, "google"))
    assert item.name == ""
    assert item.type == "int"
    assert item.text == "The return value."


def test_iter_items_without_name_with_colon():
    from astdoc.doc import iter_items_without_name

    text = "x: int\n The return value."
    item = next(iter_items_without_name(text, "numpy"))
    assert item.name == "x"
    assert item.type == "int"
    assert item.text == "The return value."


def test_iter_sections_invalid():
    from astdoc.doc import iter_sections

    text = "Args:\n \nArgs:\n x (int): A param."
    sections = list(iter_sections(text, "google"))
    assert len(sections) == 1


def test_create_admonition_see_also():
    from astdoc.doc import _create_admonition

    admonition = _create_admonition("See Also", "`astdoc`")
    assert admonition == '!!! info "See Also"\n    `astdoc`'


def test_iter_merged_items():
    from astdoc.doc import Item, iter_merged_items

    item1 = Item(name="param1", type="int", text="The first parameter.")
    item2 = Item(name="param2", type="str", text="The second parameter.")
    item3 = Item(name="param1", type="float", text="Updated first parameter.")

    merged_items = list(iter_merged_items([item1, item2], [item3]))
    assert len(merged_items) == 2
    assert merged_items[0].name == "param1"

    merged_items = list(iter_merged_items([item1], [item2, item3]))
    assert len(merged_items) == 2
    assert merged_items[0].name == "param1"


def test_iter_merged_sections_without_name():
    from astdoc.doc import Section, iter_merged_sections

    s1 = Section("", "", "A", [])
    s2 = Section("", "", "B", [])
    s3 = Section("a", "", "C", [])

    merged_sections = list(iter_merged_sections([s1, s2], [s3]))
    assert len(merged_sections) == 3

    merged_sections = list(iter_merged_sections([s1], [s2, s3]))
    assert len(merged_sections) == 3


def test_create_doc_code_block():
    from astdoc.doc import create_doc

    src = """
    docstring.

        import a

        def f():
            pass
    """
    src = inspect.cleandoc(src)
    doc = create_doc(src)
    d = """
    docstring.

    ```
    import a

    def f():
        pass
    ```
    """
    assert doc.text.rstrip() == inspect.cleandoc(d)


def test_item_clone():
    from astdoc.doc import Item

    item = Item("name", "int", "text").clone()
    assert item.name == "name"
    assert item.type == "int"
    assert item.text == "text"


def test_section_clone():
    from astdoc.doc import Item, Section

    item = Item("item", "int", "item-text")
    section = Section("section", "str", "section-text", [item]).clone()
    assert section.name == "section"
    assert section.type == "str"
    assert section.text == "section-text"
    assert section.items[0].name == "item"
    assert section.items[0].type == "int"
    assert section.items[0].text == "item-text"


def test_doc_clone():
    from astdoc.doc import Doc, Item, Section

    item = Item("item", "int", "item-text")
    section = Section("section", "str", "section-text", [item])
    doc = Doc("doc", "list", "doc-text", [section]).clone()
    assert doc.type == "list"
    assert doc.text == "doc-text"
    assert doc.sections[0].name == "section"
    assert doc.sections[0].type == "str"
    assert doc.sections[0].text == "section-text"
    assert doc.sections[0].items[0].name == "item"
    assert doc.sections[0].items[0].type == "int"
    assert doc.sections[0].items[0].text == "item-text"


def test_item_new_line():
    from astdoc.doc import create_doc

    text = "Args:\n    a (int):\n        A\n        B\n"
    doc = create_doc(text)
    section = doc.sections[0]
    assert section.items[0].text == "A\nB"
