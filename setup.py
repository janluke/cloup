#!/usr/bin/env python
from pathlib import Path

from setuptools import find_packages, setup


def make_long_description(write_file=False):
    readme = Path('README.rst').read_text(encoding='utf-8')
    # PyPI doesn't support the `raw::` directive. Skip it.
    start = readme.find('.. docs-index-start')
    long_description = readme[start:]
    if write_file:
        Path('PYPI_README.rst').write_text(long_description, encoding='utf-8')
    return long_description


setup(
    name='cloup',
    setup_requires=['setuptools_scm'],
    use_scm_version={
        'write_to': 'cloup/_version.py'
    },
    author='Gianluca Gippetto',
    author_email='gianluca.gippetto@gmail.com',
    description="Adds features to Click: option groups, constraints, subcommand "
                "sections and help themes.",
    long_description_content_type='text/x-rst',
    long_description=make_long_description(),
    url='https://github.com/janLuke/cloup',
    license="BSD 3-Clause",
    keywords=['CLI', 'click', 'argument groups', 'option groups', 'constraints',
              'help colors', 'help themes', 'help styles'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    packages=find_packages(include=['cloup', 'cloup.*']),
    zip_safe=False,
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=[
        'click >= 8.0, < 9.0',
        'typing_extensions; python_version<="3.8"',
    ],
)
