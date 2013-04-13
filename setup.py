# -*- encoding: utf8 -*-

from setuptools import setup, find_packages

setup(
    name = "toml-python",
	author = "Felipe Aragão Pires",
	author_email = "pires.a.felipe@gmail.com",
    version = "0.4",
	description = "TOML parser for python.",
    url = "https://github.com/f03lipe/toml-python",
    license = "MIT License",
    classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3',
    ],
    packages = find_packages(),
)
