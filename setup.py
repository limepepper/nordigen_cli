from setuptools import setup


setup(
    name="nordigen_cli",
    description=(
        "A simple cli for the nordigen open banking API - "
        "a Python package for interacting with nordigen API."
    ),
    license="MIT",
    url="https://github.com/konstantinstadler/country_converter",
    author="Konstantin Stadler",
    author_email="tom@limepepper.co.uk",
    version=__version__,  # noqa
    packages=["nordigen_cli"],
    entry_points={
        "console_scripts": ["nordctl = nordigen_cli.nordigen_cli:main"]
    },
    install_requires=["Flask >= 2.0.1"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Utilities",
    ],
)
