#!/usr/bin/env python3
"""
Fraud Detection Graph Agent
A production-ready FastAPI service for graph-based fraud-ring detection.
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fraud-detection-graph-agent",
    version="1.0.0",
    author="Member A - Fraud Detection Team",
    description="Graph-based fraud-ring detection service using network analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/fraud-detection",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "pylint>=2.17.0",
            "pytest>=8.3.2",
            "pytest-cov>=4.1.0",
            "httpx>=0.24.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "fraud-graph-agent=api.app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
