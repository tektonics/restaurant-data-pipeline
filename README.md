# Restaurant Data Collection Project

A comprehensive data scraping and management system designed to collect, process, and store restaurant information from various online sources including Eater.com and Google Maps.

## Overview

This project automates the collection of restaurant data, processes and standardizes the information, and stores it in a structured SQLite database. It includes features for address standardization, duplicate detection, and data enrichment through multiple sources.

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

## Features
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

## Installation

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies


## Configuration

The project uses several configuration files located in the `config/` directory:
- `config.py`: General project configuration
- `database_config.py`: Database settings and schema definitions

Key configurations can be modified in these files to adjust:
- File paths and directories
- Scraping parameters
- Database settings
- Data validation rules

