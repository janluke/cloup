#!/usr/bin/env python

from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

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
    long_description=readme,
    url='https://github.com/janLuke/cloup',
    license="BSD 3-Clause",
    keywords=['CLI', 'click', 'argument groups', 'option groups', 'constraints',
              'help colors', 'help themes', 'help styles'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(include=['cloup', 'cloup.*']),
    zip_safe=False,
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        'click >=7.1, <9.0',
        'dataclasses; python_version<="3.6"',
    ],
)
