# Changelog

## [1.1.0] - 2024-11-16

### Added
- Centralized WebDriver management system
- Unified CSV handling operations
- Directory management utilities
- Progress tracking for batch operations
- Configurable parallel processing
- Configurable pagination for Eater.com archive scraping
- Page count control through EATER_CONFIG
- Empty page detection to prevent unnecessary requests
- Enhanced progress tracking for multi-page scraping
- Automatic pagination termination on content exhaustion

### Changed
- Refactored scraper modules to use shared utilities
- Improved error handling with better recovery
- Consolidated duplicate code across modules
- Enhanced logging with better context
- Optimized parallel processing configuration
- Refactored archive scraping to support multiple pages
- Improved rate limiting between page requests
- Enhanced logging for pagination progress
- Optimized page processing with better error recovery

### Fixed
- Duplicate WebDriver initialization issues
- Inconsistent CSV writing operations
- Memory leaks in parallel processing
- Resource cleanup in error scenarios
- Directory creation race conditions
- Single page limitation in archive scraping
- Missing delay between page requests
- Incomplete archive processing
- Pagination error handling

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
