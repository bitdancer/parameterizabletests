import os
from setuptools import setup

name = 'parameterizabletests'
here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name=name,
    version='1.0.0',
    description="unittest parameterization for stdlib tests",
    long_description=long_description,
    url='https://github.com/bitdancer/extras/' + name,
    author='R. David Murray',
    author_email='rdmurray@bitdance.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        ],
    keywords='testing',
    py_modules=[name],
    )
