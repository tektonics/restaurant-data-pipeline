# Restaurant Data Collection Project

A comprehensive data scraping and management system designed to collect, process, and store restaurant information from various online sources including Eater.com and Google Maps.

## Overview

This project automates the collection of restaurant data, processes and standardizes the information, and stores it in a structured SQLite database. It includes features for address standardization, duplicate detection, and data enrichment through multiple sources.

## Features

### Data Collection
- Web scraping from Eater.com restaurant listings
- Google Maps data enhancement including:
  - Star ratings and review counts
  - Restaurant categories and price ranges
  - Geographic coordinates
  - Service options and dining features
  - Accessibility information
  - Amenities and atmosphere details
  - Payment methods and parking options
- Intelligent rate limiting and retry mechanisms
- Rotating user agents for request management
- Chrome WebDriver automation with headless mode

### Data Processing
- Address standardization and parsing with clean_and_split_address utility
- City and state validation with mapping system
- ZIP code verification and normalization
- Duplicate detection through remove_duplicates function
- Parallel processing with configurable workers:
  - Default 4 worker threads
  - Chunk-based processing for memory efficiency
  - Progress tracking per chunk
  - Automatic batch size calculation
- CSV operations with error recovery:
  - Atomic writes with newline handling
  - UTF-8 encoding support
  - Automatic directory creation
  - Row-level error handling

### Database Integration
- SQLite database with basic schema
- Single-file database structure
- Basic transaction support
- Simple data insertion with pandas DataFrame
- Error logging for database operations

## Error Handling
- Timeout protection (30-minute global timeout)
- Automatic retries for failed requests with exponential backoff
- Comprehensive logging system with separate database logs
- WebDriver recovery and session management
- Transaction rollback on failures

## Code Organization

### Utility Modules
- Centralized WebDriver management
- Unified CSV operations
- Directory structure handling
- Standardized error handling patterns
- Progress tracking and monitoring

### Processing Pipeline
- Parallel processing with 4 default workers
- Configurable chunk size based on data volume
- Memory-efficient batch processing
- Progress tracking per worker

## Project Structure

restaurant_data_project/
├── src/
│   ├── config/        # Configuration files
│   ├── scrapers/      # Web scraping modules
│   ├── data_processing/ # Data cleaning and processing
│   ├── database/      # Database operations
│   └── utils/         # Utility functions
├── data/
│   ├── raw/          # Raw scraped data
│   ├── processed/    # Cleaned and processed data
│   └── database/     # SQLite database files
├── scripts/          # Utility scripts
├── tests/           # Test files
└── logs/            # Log files

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the package and dependencies:
   ```bash
   python setup.py install
   ```

## Configuration

The project uses several configuration files:

### Main Configuration (src/config/config.py)
- Scraping parameters and delays
- User agents rotation
- Chrome WebDriver options
- Timeout configurations
- State abbreviation mappings
- Rate limiting settings

### Database Configuration (src/config/database_config.py)
- Database file paths
- Backup directory settings
- Schema definitions
- Core field specifications
- Logging configurations

### Scraping Configuration
- `pages_to_scrape`: Number of archive pages to scrape (default: 75)
- `delay.between_pages`: Delay between page requests (default: 2-5 seconds)
- `delay.between_articles`: Delay between article scrapes (default: 5-10 seconds)

Example configuration in src/config/config.py:

```python
EATER_CONFIG = {
    'pages_to_scrape': 75,  # Modify this value to scrape more or fewer pages
    'delay': {
        'between_pages': (2, 5),
        'between_articles': (5, 10)
    }
}
```

## Usage

1. Run the main data collection pipeline:
   ```bash
   python -m src.main
   ```

2. Check database status:
   ```bash
   python scripts/check_db.py
   ```

3. Process missing restaurants:
   ```bash
   python scripts/dupcheck.py
   ```

4. Enhance existing data:
   ```bash
   python scripts/enhance_send2db.py
   ```

## Dependencies

- Python >= 3.8
- pandas >= 1.3.0
- requests >= 2.26.0
- beautifulsoup4 >= 4.9.3
- selenium >= 4.0.0
- python-dotenv >= 0.19.0
- webdriver-manager == 4.0.0
- urllib3 >= 1.26.0
- pathlib >= 1.0.1

## Development

### Code Quality Tools

#### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality. To set up:

1. Install pre-commit:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. Run against all files:
   ```bash
   pre-commit run --all-files
   ```

3. Available hooks:
   - trailing-whitespace: Removes trailing whitespace
   - end-of-file-fixer: Ensures files end with a newline
   - check-yaml: Validates YAML syntax
   - check-added-large-files: Prevents large files from being committed
   - debug-statements: Checks for debugger imports
   - black: Formats Python code
   - flake8: Lints Python code

#### Black Configuration
Black is configured with default settings:
- Line length: 88 characters
- String normalization: Double quotes
- Python version: Python 3.8+

To run Black manually:
```bash
black src/ scripts/ tests/
```

#### Flake8 Configuration
Flake8 enforces PEP 8 style guide with custom settings

### WebDriver Configuration
- Centralized WebDriver management
- Automatic ChromeDriver installation
- Fallback to system ChromeDriver
- Configurable options and timeouts

## Project Status

This project is currently under active development. The core functionality is implemented and working, with ongoing improvements to data collection reliability and processing efficiency.


