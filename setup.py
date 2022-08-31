from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()
    requirements.append("setuptools_scm")

setup(
    name="Don Quijote",
    version="1.0",
    author="Philipp Stuerner",
    description="Practicing Spanish Vocabularies in Telegram",
    python_requires=">=3.6.8",
    packages=find_packages(),
)
