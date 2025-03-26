# astdoc

[![PyPI Version][pypi-v-image]][pypi-v-link]
[![Build Status][GHAction-image]][GHAction-link]
[![Coverage Status][codecov-image]][codecov-link]
[![Documentation Status][docs-image]][docs-link]
[![Python Version][python-v-image]][python-v-link]

A lightweight Python library for parsing and analyzing abstract
syntax trees (AST) and extracting docstring information.
Designed to facilitate the documentation process, astdoc provides
tools for developers to easily access, manipulate, and generate
documentation from Python code.

## Features

- **Smart Docstring Parsing**: Automatically extracts and parses docstrings
  in Google and NumPy styles
- **AST Analysis**: Deep understanding of Python code structure through AST traversal
- **Namespace Support**: Handles namespace packages and complex module structures
- **Type-Aware**: Built-in support for type hints and annotations
- **Modern Python**: Compatible with Python 3.10+ including the latest 3.13
- **Lightweight**: Minimal dependencies, focusing on core functionality

## Installation

```bash
pip install astdoc
```

## Documentation

For detailed documentation, visit
[https://daizutabi.github.io/astdoc/](https://daizutabi.github.io/astdoc/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE)
file for details.

<!-- Badges -->
[pypi-v-image]: https://img.shields.io/pypi/v/astdoc.svg
[pypi-v-link]: https://pypi.org/project/astdoc/
[GHAction-image]: https://github.com/daizutabi/astdoc/actions/workflows/ci.yaml/badge.svg?branch=main&event=push
[GHAction-link]: https://github.com/daizutabi/astdoc/actions?query=event%3Apush+branch%3Amain
[codecov-image]: https://codecov.io/github/daizutabi/astdoc/coverage.svg?branch=main
[codecov-link]: https://codecov.io/github/daizutabi/astdoc?branch=main
[docs-image]: https://img.shields.io/badge/docs-latest-blue.svg
[docs-link]: https://daizutabi.github.io/astdoc/
[python-v-image]: https://img.shields.io/pypi/pyversions/astdoc.svg
[python-v-link]: https://pypi.org/project/astdoc
