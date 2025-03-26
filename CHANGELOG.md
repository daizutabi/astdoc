# Changelog

## [1.1.5]

### Changed
- Updated project description and keywords in pyproject.toml

### Fixed
- Fixed whitespace handling in `_split_google_style_item` and `_split_numpy_style_item` functions
- Improved handling of new lines in item text

## [1.1.4]

### Added
- Added depth control to `_iter_assign_nodes` function for AST traversal
- Added new test for iterating assignment nodes in enum classes

### Changed
- Renamed test function for iterating child nodes in enum classes

## [1.1.3]

### Added
- Added tests for split_module_name function to handle namespace cases and create a new sub module

### Changed
- Fixed logic in split_module_name function to correctly handle module names and package detection

## [1.1.2]

### Added
- Added GitHub Actions workflow for publishing to PyPI
- Added MkDocs configuration and GitHub Actions for documentation deployment
- Added strict type inference for dictionaries, lists, and sets in Pyright configuration
- Extended Pyright type checking to include tests directory

### Changed
- Refactored is_package function to improve package detection and update tests for new namespace structure
- Configured Pyright type checking for source directory
- Removed unused type variable T from utils.py