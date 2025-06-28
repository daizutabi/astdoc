import ast

import pytest

from src.astdoc.doc import create_doc, get_style


def test_numpy_multiple_returns():
    source = '''
def sum_and_product(x, y):
    """Computes the sum and product of two integers

    Returns
    -------
    s : int
      sum of x and y
    p : int
      product of x and y
    """
    return x+y, x*y
'''

    node = ast.parse(source)
    assert isinstance(node.body[0], ast.FunctionDef)
    text = ast.get_docstring(node.body[0])
    assert text is not None

    assert get_style(text) == "numpy"
    doc = create_doc(text, "numpy")

    returns_section = None
    for section in doc.sections:
        if section.name == "Returns":
            returns_section = section
            break

    assert returns_section is not None
    assert len(returns_section.items) == 2

    assert returns_section.items[0].name == "s"
    assert returns_section.items[0].type == "int"
    assert returns_section.items[0].text == "sum of x and y"

    assert returns_section.items[1].name == "p"
    assert returns_section.items[1].type == "int"
    assert returns_section.items[1].text == "product of x and y"


def test_numpy_single_return():
    source = '''
def single_return():
    """Function with single return value.

    Returns
    -------
    int
        The return value.
    """
    return 1
'''

    node = ast.parse(source)
    assert isinstance(node.body[0], ast.FunctionDef)
    text = ast.get_docstring(node.body[0])
    assert text is not None

    assert get_style(text) == "numpy"
    doc = create_doc(text, "numpy")

    returns_section = None
    for section in doc.sections:
        if section.name == "Returns":
            returns_section = section
            break

    assert returns_section is not None
    assert len(returns_section.items) == 1

    assert returns_section.items[0].name == ""
    assert returns_section.items[0].type == "int"
    assert returns_section.items[0].text == "The return value."


@pytest.mark.skip(reason="Google style is not supported yet")
def test_google_multiple_returns():
    source = '''
def function_with_multiple_returns():
    """Function with multiple return values.

    Returns:
        sum (int): The first return value.
        product (str): The second return value.
    """
    return 1, "hello"
'''

    node = ast.parse(source)
    assert isinstance(node.body[0], ast.FunctionDef)
    text = ast.get_docstring(node.body[0])
    assert text is not None

    assert get_style(text) == "google"
    doc = create_doc(text, "google")

    returns_section = None
    for section in doc.sections:
        if section.name == "Returns":
            returns_section = section
            break

    assert returns_section is not None
    assert len(returns_section.items) == 2

    # Check first return value
    assert returns_section.items[0].name == "sum"
    assert returns_section.items[0].type == "int"
    assert returns_section.items[0].text == "The first return value."

    # Check second return value
    assert returns_section.items[1].name == "product"
    assert returns_section.items[1].type == "str"
    assert returns_section.items[1].text == "The second return value."


def test_google_single_return():
    """Test Google style with single return"""
    source = '''
def single_return():
    """Function with single return value.

    Returns:
        int: The return value.
    """
    return 1
'''

    node = ast.parse(source)
    assert isinstance(node.body[0], ast.FunctionDef)
    text = ast.get_docstring(node.body[0])
    assert text is not None

    assert get_style(text) == "google"
    doc = create_doc(text, "google")

    returns_section = None
    for section in doc.sections:
        if section.name == "Returns":
            returns_section = section
            break

    assert returns_section is not None
    assert len(returns_section.items) == 1

    # Check single return value
    assert returns_section.items[0].name == ""
    assert returns_section.items[0].type == "int"
    assert returns_section.items[0].text == "The return value."


def test_google_single_return_multiline():
    source = '''
def single_return():
    """Function with single return value.

    Returns:
        int: The return value.
        This can span multiple lines.
    """
    return 1
'''

    node = ast.parse(source)
    assert isinstance(node.body[0], ast.FunctionDef)
    text = ast.get_docstring(node.body[0])
    assert text is not None

    assert get_style(text) == "google"
    doc = create_doc(text, "google")

    returns_section = None
    for section in doc.sections:
        if section.name == "Returns":
            returns_section = section
            break

    assert returns_section is not None
    assert len(returns_section.items) == 1

    # Check single return value with multiline text
    item = returns_section.items[0]
    assert item.name == ""
    assert item.type == "int"
    assert item.text == "The return value.\nThis can span multiple lines."


@pytest.mark.skip(reason="Google style is not supported yet")
def test_google_single_return_multiline_with_indent():
    source = '''
def single_return():
    """Function with single return value.

    Returns:
        int: The return value.
            This can span multiple lines.
    """
    return 1
'''

    node = ast.parse(source)
    assert isinstance(node.body[0], ast.FunctionDef)
    text = ast.get_docstring(node.body[0])
    assert text is not None

    assert get_style(text) == "google"
    doc = create_doc(text, "google")

    returns_section = None
    for section in doc.sections:
        if section.name == "Returns":
            returns_section = section
            break

    assert returns_section is not None
    assert len(returns_section.items) == 1

    # Check single return value with multiline text
    item = returns_section.items[0]
    assert item.name == ""
    assert item.type == "int"
    assert item.text == "The return value.\nThis can span multiple lines."
