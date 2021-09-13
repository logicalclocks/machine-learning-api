import os
import imp
from setuptools import setup, find_packages


__version__ = imp.load_source(
    "hsml.version", os.path.join("hsml", "version.py")
).__version__


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="hsml",
    version=__version__,
    install_requires=[],
    extras_require={
        "dev": [
            "pytest",
            "flake8",
            "black"],
        "docs": [
            "mkdocs==1.1.2",
            "mkdocs-material==6.2.2",
            "mike==0.5.5",
            "keras-autodoc",
            "markdown-include"]
    },
    author="Logical Clocks AB",
    author_email="robin@logicalclocks.com",
    description="HSML: An environment independent client to interact with the Hopsworks Experiments, Model Registry and Serving service",
    license="Apache License 2.0",
    keywords="Hopsworks, ML, Models, Machine Learning Models, TensorFlow, PyTorch, Machine Learning, MLOps, DataOps",
    url="https://github.com/logicalclocks/machine-learning-api",
    download_url="https://github.com/logicalclocks/machine-learning-api/releases/tag/"
    + __version__,
    packages=find_packages(),
    long_description=read("../README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
    ],
)
