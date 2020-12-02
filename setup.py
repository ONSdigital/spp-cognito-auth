import sys

from setuptools import setup

assert sys.version_info >= (3, 6, 0), "spp_cognito_auth requires Python 3.6+"
from pathlib import Path  # noqa E402

CURRENT_DIR = Path(__file__).parent
sys.path.insert(0, str(CURRENT_DIR))  # for setuptools.build_meta

setup(
    name="spp_cognito_auth",
    description="A python library to add cognito auth to apps",
    url="https://github.com/ONSdigital/spp-cognito-auth",
    license="MIT",
    packages=["spp_cognito_auth"],
    package_dir={"": "."},
    package_data={"spp_cognito_auth": ["py.typed"]},
    python_requires=">=3.6",
    install_requires=[
        "Authlib>=0.15.2",
        "requests>=2.25.0",
        "CacheControl>=0.12.6",
        "Flask>=1.1.2",
    ],
    test_suite="tests",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
