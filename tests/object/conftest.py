import ast

import pytest

from astdoc.ast import iter_child_nodes
from astdoc.utils import get_module_node


@pytest.fixture(scope="module")
def google():
    return get_module_node("examples._styles.google")


@pytest.fixture(scope="module")
def get(google):
    def get(name, *rest, node=google):
        for child in iter_child_nodes(node):
            if not isinstance(child, ast.FunctionDef | ast.ClassDef):
                continue
            if child.name == name:
                if not rest:
                    return child
                return get(*rest, node=child)
        raise NameError

    return get
