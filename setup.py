"""
Setup script for Sheriff of Nottingham game
Allows the project to be installed in development mode for testing
"""

from setuptools import setup, find_packages

setup(
    name="sheriff-of-nottingham",
    version="0.1.0",
    description="Sheriff of Nottingham board game implementation",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.10",
    install_requires=[
        "pygame>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.0.0",
        ],
    },
)
