# Changelog

## [1.1.0] - 2024-03-16

### Added
- Centralized WebDriver management system
- Unified CSV handling operations
- Directory management utilities
- Progress tracking for batch operations
- Configurable parallel processing

### Changed
- Refactored scraper modules to use shared utilities
- Improved error handling with better recovery
- Consolidated duplicate code across modules
- Enhanced logging with better context
- Optimized parallel processing configuration

### Fixed
- Duplicate WebDriver initialization issues
- Inconsistent CSV writing operations
- Memory leaks in parallel processing
- Resource cleanup in error scenarios
- Directory creation race conditions

### Technical Debt
- Removed redundant WebDriver setup code
- Consolidated CSV operations
- Unified configuration management
- Standardized error handling patterns
- Improved resource cleanup

### Dependencies
- Added webdriver-manager for better ChromeDriver handling
- Updated selenium configuration for better stability
- Enhanced pandas usage for memory efficiency

### Documentation
- Updated README with new architecture details
- Added code organization section
- Improved installation instructions
- Added parallel processing configuration guide
- Enhanced troubleshooting documentation
