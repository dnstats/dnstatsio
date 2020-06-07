import os
import re

import setuptools

ROOT = os.path.dirname(__file__)


def parse_requirements(filename):
    requirements = []
    for line in open(filename, 'r').read().split('\n'):
        # Skip comments
        if re.match(r'(\s*#)|(\s*#)', line):
            continue
        requirements.append(line)

    return requirements


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dnstats",
    version="0.0.1",
    author="Matthew Burket",
    author_email="hello@dnstats.io",
    description="Daily DNS scanning of top websites on DNS.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dnstats.io",
    packages=setuptools.find_packages(),
    install_requires=parse_requirements(os.path.join(ROOT, '..', 'requirements.txt')),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: System :: Networking",
        "Intended Audience :: Information Technology"
    ],
    python_requires='>=3.6',
)
