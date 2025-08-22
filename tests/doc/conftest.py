import ast
from ast import AST, ClassDef, FunctionDef
from collections.abc import Callable

import pytest

from astdoc.ast import iter_child_nodes
from astdoc.utils import get_module_node


@pytest.fixture(scope="module")
def google():
    return get_module_node("examples._styles.google")


@pytest.fixture(scope="module")
def numpy():
    return get_module_node("examples._styles.numpy")


@pytest.fixture(scope="module")
def get_node():
    def get_node(node: AST, name: str):
        for child in iter_child_nodes(node):
            if not isinstance(child, FunctionDef | ClassDef):
                continue
            if child.name == name:
                return child
        raise NameError

    return get_node


@pytest.fixture(scope="module")
def get(get_node: Callable[[AST, str], FunctionDef | ClassDef]):
    def get(node: AST, name: str):
        return ast.get_docstring(get_node(node, name))

    return get
