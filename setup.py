"""Setup configuration for Cascade."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cascade-cli",
    version="0.1.0",
    author="Eve",
    description="Beautiful multi-model AI assistant CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cascade",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
        "pyyaml>=6.0",
        "httpx>=0.24.0",
        "pygments>=2.14.0",
    ],
    entry_points={
        "console_scripts": [
            "cascade=cascade.cli:cli",
        ],
    },
)
