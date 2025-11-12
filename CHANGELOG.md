# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of vpype-plotty plugin
- Core commands: plotty-add, plotty-queue, plotty-status, plotty-list
- ploTTY workspace detection and configuration management
- Standalone mode support (works without ploTTY installation)
- Comprehensive test suite with >90% coverage
- Integration with vsketch and vpype workflows
- Multiple output formats (table, JSON, CSV)
- Optimization presets (fast, default, hq)
- Batch processing examples
- CI/CD pipeline with GitHub Actions

### Features
- **plotty-add**: Add documents to ploTTY job queue
- **plotty-queue**: Queue existing ploTTY jobs for plotting
- **plotty-status**: Check job status with multiple output formats
- **plotty-list**: List ploTTY jobs with filtering options
- **Configuration**: Automatic ploTTY workspace detection
- **Integration**: Seamless vsketch and vpype integration
- **Standalone**: Works without ploTTY installation

### Documentation
- Comprehensive README with installation and usage instructions
- Example scripts for vsketch integration, batch processing, and standalone usage
- API documentation for all modules and functions
- Development guidelines and contribution instructions

### Testing
- Unit tests for all core functionality
- Integration tests with mocked ploTTY dependencies
- Test coverage reporting with pytest-cov
- Automated testing on Python 3.11, 3.12, and 3.13

## [0.1.0] - 2024-01-XX

### Added
- Initial release of vpype-plotty
- Basic ploTTY integration functionality
- Support for vpype plugin system
- Core command implementation
- Configuration management
- Documentation and examples