from pathlib import Path
from setuptools import setup, find_packages

def parse_requirements(filename="requirements.txt"):
    lines = Path(filename).read_text().splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.startswith("#")
    ]


setup(
    name="bunt",
    version="1.0",
    description="A module for segmenting and cropping images of fashion products.",
    author="Valentina Feruere",
    author_email="valentinaferuere@close.com.co",
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "bunt=bunt.cli:cli",
        ],
    },
)
