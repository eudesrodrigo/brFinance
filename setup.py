from setuptools import setup, find_packages

setup(
    name='brfinance',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='A Python package for webscraping financial data brazilian sources such as CVM, Banco Central, B3, ANBIMA, etc.',
    long_description=open('README.md').read(),
    install_requires=['numpy', 'beautifulsoup4', 'bs4', 'certifi', 'charset-normalizer', 'colorama', 'configparser', 'crayons', 'fake-useragent',
                      'idna', 'lxml', 'numpy', 'pandas', 'python-dateutil', 'pytz', 'requests', 'selenium', 'six', 'soupsieve', 'urllib3', 'webdriver-manager'],
    url='https://github.com/BillMills/python-package-example',
    author='Eudes Rodrigo Nunes de Oliveira',
    author_email='eudesrodrigo@outlook.com'
)
