from setuptools import setup, find_packages
import os
from pathlib import Path

# Create necessary directories
data_dirs = [
    'data/raw',
    'data/processed',
    'data/database',
    'logs'
]

for dir_path in data_dirs:
    Path(dir_path).mkdir(parents=True, exist_ok=True)

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
        'pathlib>=1.0.1',
    ],
    python_requires='>=3.8',
)
