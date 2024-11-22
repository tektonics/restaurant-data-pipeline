from setuptools import setup, find_packages
import os
from pathlib import Path
from src.utils.directory_manager import ensure_project_directories

ensure_project_directories()

setup(
    name="restaurant-data-pipeline",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'pandas>=1.3.0',
        'requests>=2.26.0',
        'beautifulsoup4>=4.9.3',
        'selenium>=4.0.0',
        'python-dotenv>=0.19.0',
        'webdriver-manager>=4.0.0',
    ],
    python_requires='>=3.8',
)
