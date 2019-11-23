from setuptools import find_packages, setup


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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires=[],
    packages=find_packages(),
    package_data={
        '': ['*.*'],
    },
    test_suite='lalr.tests.suite',
)
