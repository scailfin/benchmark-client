from setuptools import setup


install_requires=[
    'future',
    'Click',
    'benchmark-templates'
]


tests_require = [
    'coverage>=4.0',
    'coveralls',
    'nose'
]


extras_require = {
    'docs': [
        'Sphinx',
        'sphinx-rtd-theme'
    ],
    'tests': tests_require,
}


setup(
    name='benchmark-client',
    version='0.1.0',
    description='Client for Reproducible Benchmarks for Data Analysis Engine API',
    keywords='reproducibility benchmarks data analysis',
    license='MIT',
    packages=['benchclient'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'rob = benchclient.cli.base:cli',
        ]
    },
    test_suite='nose.collector',
    extras_require=extras_require,
    tests_require=tests_require,
    install_requires=install_requires
)
