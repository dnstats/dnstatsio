import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dnstats", # Replace with your own username
    version="0.0.1",
    author="Matthew Burket",
    author_email="hello@dnstats.io",
    description="Daily DNS scanning of top websites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://dnstats.io",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)