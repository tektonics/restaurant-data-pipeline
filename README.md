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
- Address standardization and parsing
- City and state validation with abbreviation mapping
- ZIP code verification and normalization
- Multi-level duplicate detection
- Progressive data enhancement
- Batch processing with parallel execution

### Database Integration
- SQLite database with optimized schema
- Automated backup system with timestamped copies
- Transaction management and rollback support
- Efficient indexing for common queries
- Structured data validation

## Error Handling
- Timeout protection (30-minute global timeout)
- Automatic retries for failed requests with exponential backoff
- Comprehensive logging system with separate database logs
- WebDriver recovery and session management
- Transaction rollback on failures

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

## Development

The project uses several development tools:
- pre-commit hooks for code quality
- Black for code formatting
- Flake8 for linting
- Comprehensive .gitignore configuration
- Structured logging throughout

## Project Status

This project is currently under active development. The core functionality is implemented and working, with ongoing improvements to data collection reliability and processing efficiency.
