import sys

from setuptools import setup, find_packages


install_requires = []
if sys.version_info < (3, 5):
    install_requires += [
        'mypy-lang',
    ]


setup(
    name='lalr',
    url='https://github.com/bwhmather/python-lalr',
    version='0.0.1',
    author='Ben Mather',
    author_email='bwhmather@bwhmather.com',
    maintainer='Ben Mather',
    license='BSD',
    description=(
        "A pure python LALR parser generator"
    ),
    long_description=__doc__,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires=install_requires,
    packages=find_packages(),
    package_data={
        '': ['*.*'],
    },
    test_suite='lalr.tests.suite',
)
