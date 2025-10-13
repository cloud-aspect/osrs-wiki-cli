#!/usr/bin/env python3
"""Setup configuration for osrs-wiki-cli."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="osrs-wiki-cli",
    version="1.0.0",
    description="Modern CLI utility for extracting structured data from Old School RuneScape Wiki",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="cloud-aspect",
    author_email="",
    url="https://github.com/cloud-aspect/osrs-wiki-cli",
    project_urls={
        "Bug Reports": "https://github.com/cloud-aspect/osrs-wiki-cli/issues",
        "Source": "https://github.com/cloud-aspect/osrs-wiki-cli",
        "Documentation": "https://github.com/cloud-aspect/osrs-wiki-cli/blob/main/docs/README.md",
    },
    py_modules=["wiki_tool"],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "osrs-wiki-cli=wiki_tool:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords=[
        "osrs",
        "runescape",
        "wiki",
        "cli",
        "data-extraction",
        "mediawiki",
        "runelite",
        "gaming-tools"
    ],
    license="MIT",
)