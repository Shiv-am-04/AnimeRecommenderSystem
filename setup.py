from setuptools import setup,find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Anime-Recommender",
    version="0.1",
    author="Shivam",
    packages=find_packages(),
    install_requires = requirements,
)