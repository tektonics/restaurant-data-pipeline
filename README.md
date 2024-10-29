# Restaurant Data Collection Project

A comprehensive data scraping and management system designed to collect, process, and store restaurant information from various online sources including Eater.com and Google Maps.

## Overview

This project automates the collection of restaurant data, processes and standardizes the information, and stores it in a structured SQLite database. It includes features for address standardization, duplicate detection, and data enrichment through multiple sources.

## Features

### Data Collection
- Web scraping from Eater.com restaurant listings
- Google Maps data enhancement including:
  - Star ratings and review counts
  - Restaurant categories
  - Geographic coordinates
  - Service options and amenities
- Instagram profile information extraction
- Intelligent rate limiting and retry mechanisms
- Rotating user agents for request management

### Data Processing
- Address standardization and parsing
- City and state validation
- ZIP code verification
- Duplicate detection and removal
- Data validation and enhancement

### Database Integration
- SQLite database with optimized schema
- Automated backup system
- Efficient querying capabilities
- Structured data storage

## Error Handling

- Automatic retries for failed requests
- Comprehensive logging system
- Timeout protection for long-running operations
- Database transaction management

## Project Status

This project is currently under active development. License and contribution guidelines will be added in future updates.

## Project Structure

restaurant_data_project/
├── config/             # Configuration files
│   ├── config.py      # General configuration
│   └── database_config.py # Database settings
├── data/              # Data storage
│   ├── raw/           # Raw scraped data
│   ├── processed/     # Cleaned and processed data
│   └── database/      # SQLite database files
├── src/               # Source code
│   ├── scrapers/      # Web scraping modules
│   ├── data_processing/ # Data cleaning and processing
│   ├── database/      # Database operations
│   └── utils/         # Utility functions
├── tests/             # Test files
├── notebooks/         # Jupyter notebooks
└── logs/              # Log files

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

### Main Configuration (config.py)
- Scraping parameters
- User agents and request settings
- Chrome WebDriver options
- Timeout configurations
- Data processing rules

### Database Configuration (database_config.py)
- Database file paths
- Backup settings
- Schema definitions
- Core field specifications

## Usage

1. Run the main script to start data collection:
   ```bash
   python -m src.main
   ```

2. Check database status:
   ```bash
   python scripts/check_db.py
   ```

## Dependencies

- Python >= 3.8
- pandas >= 1.3.0
- requests >= 2.26.0
- beautifulsoup4 >= 4.9.3
- selenium >= 4.0.0
- python-dotenv >= 0.19.0

## Development

The project uses several development tools:
- pre-commit hooks for code quality
- Black for code formatting
- Flake8 for linting

Install development dependencies:
