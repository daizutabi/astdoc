import doctest
import inspect
import re

import pytest


@pytest.mark.parametrize(
    ("text", "results"),
    [
        ("abcXdef", [(0, 0, 3), (2, 4, 7)]),
        ("XabcXdefX", [(1, 1, 4), (3, 5, 8)]),
        ("abc\n", [(0, 0, 4)]),
    ],
)
def test_iter(text, results):
    from astdoc.markdown import _iter

    x = list(_iter(re.compile("X"), text))
    for i, start, end in results:
        assert x[i] == (start, end)


@pytest.mark.parametrize(
    ("text", "pos", "results"),
    [
        ("abcXdef", 1, [(0, 1, 3), (2, 4, 7)]),
        ("XabcXdefX", 2, [(0, 2, 4), (2, 5, 8)]),
    ],
)
def test_iter_pos(text, pos, results):
    from astdoc.markdown import _iter

    x = list(_iter(re.compile("X"), text, pos=pos))
    for i, start, end in results:
        assert x[i] == (start, end)


def test_iter_match_only():
    from astdoc.markdown import _iter

    x = list(_iter(re.compile("X"), "X"))
    assert len(x) == 1
    assert isinstance(x[0], re.Match)


def test_iter_fenced_codes():
    from astdoc.markdown import _iter_fenced_codes

    text = "abc\n~~~~x\n```\nx\n```\n~~~~\ndef\n"
    x = list(_iter_fenced_codes(text))
    assert len(x) == 3
    assert text[x[0][0] : x[0][1]] == "abc\n"
    assert text[x[2][0] : x[2][1]] == "\ndef\n"


@pytest.mark.parametrize(("suffix", "n"), [("", 2), ("\n", 3)])
def test_iter_fenced_codes_suffix(suffix, n):
    from astdoc.markdown import _iter_fenced_codes

    text = f"abc\n~~~~x\n```\nx\n```\n~~~~{suffix}"
    x = list(_iter_fenced_codes(text))
    assert len(x) == n
    assert text[x[0][0] : x[0][1]] == "abc\n"


def test_iter_fenced_codes_none():
    from astdoc.markdown import _iter_fenced_codes

    assert list(_iter_fenced_codes("abc\n")) == [(0, 4)]


@pytest.fixture(scope="module")
def examples_text():
    text = """
    X
      >>> a = 1
      >>> # comment

      Y
        >>> a  # doctest: aaa
        1
        >>>
        >>> a = 1

    >>> a
    1

    Z
    """
    return inspect.cleandoc(text)


@pytest.fixture(scope="module")
def examples(examples_text):
    from astdoc.markdown import _iter_examples

    return list(_iter_examples(examples_text))


def test_iter_examples_len(examples):
    assert len(examples) == 10


@pytest.mark.parametrize(
    ("i", "source"),
    [(0, "X\n"), (3, "\n  Y\n"), (7, "\n"), (9, "\nZ")],
)
def test_iter_examples_str(examples, i, source):
    assert examples[i] == source


@pytest.mark.parametrize(
    ("i", "source", "indent"),
    [
        (1, "a = 1\n", 2),
        (2, "# comment\n", 2),
        (4, "a\n", 4),
        (5, "\n", 4),
        (6, "a = 1\n", 4),
        (8, "a\n", 0),
    ],
)
def test_iter_examples_example(examples, i, source, indent):
    example = examples[i]
    assert isinstance(example, doctest.Example)
    assert example.source == source
    assert example.indent == indent


def test_iter_examples_item_example_want(examples):
    assert examples[8].want == "1\n"


def test_iter_example_one():
    from astdoc.markdown import _iter_examples

    x = list(_iter_examples(">>> abc\n"))
    assert len(x) == 1
    assert isinstance(x[0], doctest.Example)


@pytest.mark.parametrize("text", ["a", "a\n", "abc\ndef\n", "abc\ndef", ">>> abc"])
def test_iter_examples_empty(text):
    from astdoc.markdown import _iter_examples

    assert list(_iter_examples(text)) == [text]


def test_iter_example_lists(examples_text):
    from astdoc.markdown import _iter_example_lists

    x = list(_iter_example_lists(examples_text))
    assert len(x) == 8


@pytest.fixture(scope="module")
def convert_examples():
    from astdoc.markdown import _iter_example_lists

    src = """
    >>>  1 # input
    1
      >>> a = 2
      >>> a
      2
    >>> a = 3
    """
    src = inspect.cleandoc(src)
    return list(_iter_example_lists(src))


@pytest.fixture(scope="module")
def converted_examples(convert_examples):
    from astdoc.markdown import _convert_examples

    return [_convert_examples(e) for e in convert_examples]


def test_convert_examples_len(converted_examples):
    assert len(converted_examples) == 3


@pytest.mark.parametrize(
    ("i", "text"),
    [
        (0, "input}\n 1 #"),
        (0, "output}\n1\n```\n"),
        (1, "input}\n  a = 2\n  a\n  ```\n"),
        (1, "output}\n  2\n  ```\n"),
        (2, "input}\na = 3\n```\n"),
    ],
)
def test_convert_examples(converted_examples, i, text):
    assert text in converted_examples[i]


@pytest.mark.parametrize(
    ("text", "first"),
    [
        ("\n a\n b\n\n c\nd\n", "\n a\n b\n\n c\n"),
        ("\n a\n b\n\n c\n", "\n a\n b\n\n c\n"),
        ("a\nb\n", ""),
    ],
)
def test_split_block(text, first):
    from astdoc.markdown import _split_block

    x, y = _split_block(text, 0)
    assert x == first
    assert f"{x}{y}" == text


def test_iter_literal_block():
    from astdoc.markdown import _iter_literal_block

    src = " x\n a\n\n\n     b\n\n     c\n\nd\n"
    x = "".join(list(_iter_literal_block(src)))
    assert x == " x\n a\n\n\n ```\n b\n\n c\n ```\n\nd\n"


def test_iter_literal_block_indent():
    from astdoc.markdown import _iter_literal_block

    src = """
    docstring.

        import a

        def f():
            pass
    """
    src = inspect.cleandoc(src)
    x = "".join(list(_iter_literal_block(src)))
    assert "```\nimport a\n" in x
    assert "    pass\n```" in x


def test_convert_code_block():
    from astdoc.markdown import convert_code_block

    src = """
    ```
    ab

        d
    x
    ```
      x

          x

          y

      >>> 1
      1
    """
    src = inspect.cleandoc(src)
    m = convert_code_block(src)
    assert "```\nab\n\n    d\nx\n```\n" in m
    assert "  x\n\n  ```\n  x\n\n  y\n  ```\n" in m
    assert "\n  ```{.python" in m


def test_convert_literal_block_with_directive():
    from astdoc.markdown import convert_code_block

    src = """
    a
      .. code-block:: python

          a
      d
      .. note::

          a
      d

          b
    """
    src = inspect.cleandoc(src)
    m = convert_code_block(src)
    assert m.startswith("a\n  ```python\n  a\n  ```\n  d\n")
    assert "  .. note::\n\n      a" in m
    assert m.endswith("  d\n\n  ```\n  b\n  ```\n")


def test_convert_example_new_line():
    from astdoc.markdown import convert_code_block

    src1 = """
    a
      >>> 1
      1

      >>> 2
      2
    """
    src2 = """
    a
      >>> 1
      1
      >>> 2
      2
    """
    src1 = inspect.cleandoc(src1)
    src2 = inspect.cleandoc(src2)
    assert convert_code_block(src1) == convert_code_block(src2)


def test_convert_code_block_doctest():
    from astdoc.markdown import convert_code_block

    text = "a\n\n    >>> b\n\nc"
    result = convert_code_block(text)
    assert "a\n\n    ```{.python" in result
    assert "\n    b\n    ```\n" in result


def test_convert_code_block_doctest_without_blank_line():
    from astdoc.markdown import convert_code_block

    text = "a\n\n    >>> b\nc"
    expected = "a\n\n```\n>>> b\n```\nc\n"
    assert convert_code_block(text) == expected


def test_set_example_class():
    from astdoc.markdown import EXAMPLE_CLASS, convert_code_block, set_example_class

    input_class = EXAMPLE_CLASS["input"]
    output_class = EXAMPLE_CLASS["output"]

    set_example_class("input", "output")

    text = "a\n>>> b\n1\n>>> c\n2\n"
    text = convert_code_block(text)
    assert "```{.python .input}" in text
    assert "```{.text .output}" in text

    EXAMPLE_CLASS["input"] = input_class
    EXAMPLE_CLASS["output"] = output_class


def test_finditer():
    from astdoc.markdown import _finditer, convert_code_block

    pattern = re.compile(r"^(?P<pre>#* *)(?P<name>:::.*)$", re.MULTILINE)
    src = """
    ```
    # ::: a
    ```
    ## ::: b
    ::: c
    >>> "::: d"
    ::: d

    a

        ::: e
    f
    """
    src = inspect.cleandoc(src)
    src = convert_code_block(src)
    x = list(_finditer(pattern, src))
    assert isinstance(x[2], re.Match)
    assert isinstance(x[4], re.Match)


def test_sub():
    from astdoc.markdown import convert_code_block, sub

    pattern = re.compile(r"^(?P<pre>#* *)(?P<name>:::.*)$", re.MULTILINE)
    src = """
    ```
    # ::: a
    ```
    ## ::: b
    ::: c
    >>> "::: d"
    ::: d

    ::: e
    f
    """
    src = inspect.cleandoc(src)
    src = convert_code_block(src)

    def rel(m: re.Match):
        name = m.group("name")
        return f"xxx{name}xxx"

    m = sub(pattern, rel, src)
    assert m.startswith("```\n# ::: a\n```\nxxx::: bxxx\nxxx::: cxxx\n```{.python")
    assert m.endswith("output}\n::: d\n```\n\nxxx::: exxx\nf")


def test_sub_match():
    from astdoc.markdown import sub

    pattern = re.compile("X")
    src = "aXb"

    def rel(m: re.Match):
        name = m.group()
        return f"_{name}_"

    m = sub(pattern, rel, src)
    assert m == "a_X_b"


def test_find_iter():
    from astdoc.markdown import _finditer

    pattern = re.compile("X")
    src = "a\n```\nX\n```\nb"

    x = list(_finditer(pattern, src))
    assert x == [(0, 2), (2, 11), (11, 13)]


def test_find_iter_section():
    from astdoc.markdown import _finditer

    pattern = re.compile(r"\n\n\S")
    src = "a\n\nb\n\n ```\n X\n ```\n\nc"
    x = [m for m in _finditer(pattern, src) if isinstance(m, re.Match)]
    assert len(x) == 2


def test_sub_not_match():
    from astdoc.markdown import sub

    pattern = re.compile("X")
    src = "a\n```\nX\n```\nb"

    def rel(m: re.Match):
        name = m.group()
        return f"_{name}_"

    assert sub(pattern, rel, src) == src
