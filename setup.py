from setuptools import find_packages,setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name = "Anime Recommender System",
    version = "0.1",
    author = "Ahmad Majdi",
    packages = find_packages(),
    install_requires = requirements,
)
