import sys

import setuptools

if sys.version_info < (3, 7):
    raise RuntimeError('bolsa requires Python 3.7+')

with open('README.md', 'r') as fh:
    long_description = fh.read()

install_requires = [
    'aiohttp>=3.6.2,<4.0.0',
    'requests',
    'pandas',
    'beautifulsoup4',
    'lxml'
]


setuptools.setup(
    name='brfinance',
    version='0.0.9',
    packages=setuptools.find_packages(),
    python_requires='>=3.7.*',
    author='Eudes Rodrigo Nunes de Oliveira',
    author_email='eudesrodrigo@outlook.com',
    description=(
        'Biblioteca em Python com o objetivo de facilitar o acesso a '
        'dados financeiros periódicos de empresas brasileiras(B3/CVM).'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/eudesrodrigo/brFinance',
    download_url='https://github.com/eudesrodrigo/brFinance/archive/refs/tags/0.0.5.tar.gz',
    install_requires=install_requires,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows'
    ],
)
