import os.path

from setuptools import setup, find_packages


def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()


with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    dependencies = f.read().splitlines()

setup(
    name="octopod",
    version="0.0.1",
    description="Octopod API client",
    packages=find_packages(),
    py_modules=['cli', 'octopod_cli'],
    entry_points={'console_scripts': ['octo=cli:main']},
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.12",
    ],
    url="https://github.com/GalateaBio/octopod-cli",
    author="Galatea Bio",
    author_email="info@galatea.bio",
    install_requires=dependencies,
)
