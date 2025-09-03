"""
Setup configuration for qubit-energy-adapters package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qubit-energy-adapters",
    version="0.1.0",
    author="Qubit Energy Foundation",
    author_email="dev@qubit.energy",
    description="Data transformation and normalization adapters for energy data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qubit-foundation/qubit-energy-adapters",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "jsonschema>=4.17.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    dependency_links=[
        "git+https://github.com/qubit-foundation/qubit-energy-schemas.git#egg=qubit-energy-schemas"
    ],
)