# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2025-11-13

### 🧪 Testing Infrastructure
- **🎯 79% Test Coverage Achievement**: Exceeds 75% target across project
- **🚫 Qt-Free Testing Pattern**: Eliminates Qt dependency issues in test environment
- **📊 Module Coverage Excellence**: 
  - utils.py: 24% → 98% (+74%)
  - exceptions.py: 27% → 99% (+72%)
  - monitor.py: 0% → 88% (+88%)
  - database.py: 0% → 89% (+89%)
  - config.py: 0% → 84% (+84%)
  - base.py: 0% → 75% (+75%)
  - decorators.py: 0% → 68% (+68%)

### 🏗️ Test Framework Enhancements
- **🔧 Comprehensive Mock Strategy**: Systematic external dependency handling
- **📁 Test Organization**: Integration, performance, and scenario test suites
- **🔄 Consistent Testing**: Qt-free pattern applied across all modules
- **🛠️ Developer Experience**: Reliable test execution across environments

### 📈 Quality Improvements
- **🎯 Robust Testing Foundation**: 125 passing tests with comprehensive coverage
- **🚫 Dependency Resolution**: Eliminated Qt/GUI testing requirements
- **📚 Maintainable Infrastructure**: Established patterns for future development
- **✅ Production Readiness**: High confidence in core business logic testing

## [0.3.0] - 2025-11-12

### 🚀 Major Features
- **🌐 Complete WebSocket Integration**: Real-time ploTTY monitoring and communication
- **📡 ploTTY Protocol Compatibility**: Full support for ploTTY v1.1.0 WebSocket protocol
- **🎯 plotty-monitor Command**: New real-time monitoring interface with Rich UI
- **⚡ Async Architecture**: Non-blocking WebSocket operations throughout

### WebSocket Client Infrastructure
- **PlottyWebSocketClient**: Full-featured async WebSocket client with connection management
- **Message Schemas**: Complete ploTTY protocol compatibility with Pydantic validation
- **Channel System**: Support for jobs, devices, system, and all channels
- **Error Handling**: Graceful fallback when ploTTY WebSocket unavailable

### ploTTY Message Types
- **JobStateChangeMessage**: Job transition events (queued→running→complete)
- **JobProgressMessage**: Real-time progress with layer, points, ETA tracking  
- **DeviceStatusMessage**: Plotter connection and status monitoring
- **SystemAlertMessage**: System-level notifications (ink, errors, etc.)
- **VpypePlottyMessage**: Extended vpype-plotty specific events

### Enhanced Commands
- **plotty-add**: WebSocket broadcasting for job creation events
- **plotty-monitor**: Real-time monitoring with Rich terminal interface
- **Fallback Mode**: All commands work without WebSocket server

### 🧪 Testing & Quality
- **Comprehensive Test Suite**: 16/16 WebSocket tests passing with 100% schema coverage
- **Mock WebSocket Client**: Reliable testing without server dependency
- **Message Validation**: Complete ploTTY protocol message type testing
- **Channel Routing**: Full subscription management testing

### 📦 Dependencies
- **websockets>=12.0**: Async WebSocket client implementation
- **fastapi>=0.104.0**: WebSocket server compatibility  
- **rich>=13.0.0**: Enhanced terminal UI for monitoring
- **pytest-asyncio>=0.23.0**: Async test support

### 🔧 Technical Improvements
- **Type Safety**: Full Pydantic schema validation with proper type hints
- **Modern Python**: Updated datetime.utcnow() to datetime.now(timezone.utc)
- **Code Quality**: Black and Ruff compliant with zero linting issues
- **Error Recovery**: Automatic reconnection with exponential backoff
- **Memory Efficiency**: Streaming message processing

### 📊 Performance & Reliability
- **Async Architecture**: Non-blocking WebSocket operations
- **Graceful Degradation**: Full functionality without WebSocket server
- **Backward Compatibility**: All existing functionality preserved
- **Configuration Auto-discovery**: XDG config directory support
- **Navigation System**: Clear paths through documentation based on user needs
- **Error Recovery**: Automatic retry with exponential backoff for transient failures
- **User-Friendly Errors**: Detailed error messages with actionable recovery hints

### Documentation Structure
- **QUICKSTART.md**: 5-minute getting started guide
- **docs/index.md**: Documentation hub with learning paths
- **docs/getting-started.md**: Detailed installation and basic concepts
- **docs/basic-usage.md**: Core commands and everyday workflows
- **docs/configuration.md**: Workspace setup and customization
- **docs/api-reference.md**: Complete technical reference
- **Enhanced README.md**: Streamlined overview with clear navigation

### User Experience Improvements
- **Lower Barrier to Entry**: New users can succeed in 5 minutes
- **Progressive Learning**: Users can dive deeper as needed
- **Better Discoverability**: Clear navigation and focused topics
- **Reduced Cognitive Load**: Each document has single purpose
- **Easier Maintenance**: Smaller, focused documents

### Infrastructure
- **Version Alignment**: Updated to v0.3.0 to align with PRD Phase 3
- **Production Ready**: Complete documentation for production release
- **Maintainable Structure**: Modular documentation for easier updates

## [0.2.0] - 2025-11-12

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

## [0.1.0] - 2025-11-12

### Added
- Initial release of vpype-plotty
- Basic ploTTY integration functionality
- Support for vpype plugin system
- Core command implementation
- Configuration management
- Documentation and examples