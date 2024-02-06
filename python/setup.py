#
#   Copyright 2021 Logical Clocks AB
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import os
from importlib.machinery import SourceFileLoader
from setuptools import setup, find_packages


__version__ = (
    SourceFileLoader("hsml.version", os.path.join("hsml", "version.py"))
    .load_module()
    .__version__
)


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="hsml",
    version=__version__,
    install_requires=[
        "pyhumps==1.6.1",
        "requests",
        "furl",
        "boto3",
        "pandas",
        "numpy",
        "pyjks",
        "mock",
        "tqdm",
    ],
    extras_require={
        "dev": ["pytest", "flake8", "black"],
        "docs": [
            "mkdocs==1.3.0",
            "mkdocs-material==8.2.8",
            "mike==1.1.2",
            "sphinx==3.5.4",
            "keras_autodoc @ git+https://git@github.com/logicalclocks/keras-autodoc@split-tags-properties",
            "markdown-include",
            "markdown==3.3.7",
            "pymdown-extensions",
        ],
    },
    author="Logical Clocks AB",
    author_email="robin@logicalclocks.com",
    description="HSML: An environment independent client to interact with the Hopsworks Model Registry",
    license="Apache License 2.0",
    keywords="Hopsworks, ML, Models, Machine Learning Models, Model Registry, TensorFlow, PyTorch, Machine Learning, MLOps, DataOps",
    url="https://github.com/logicalclocks/machine-learning-api",
    download_url="https://github.com/logicalclocks/machine-learning-api/releases/tag/"
    + __version__,
    packages=find_packages(),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
    ],
)
