[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<br />
<p align="center">
  <a href="https://github.com/eudesrodrigo/brFinance">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">brFinance</h3>

  <p align="center">
    A Python web scraping package to simplify access to financial data of brazilian companies and institutions.
    <br />
    <!--a href="https://github.com/othneildrew/Best-README-Template"><strong>Explore the docs »</strong></a>
    <br /-->
    <br />
    <a href="https://github.com/eudesrodrigo/brFinance/blob/master/Example.ipynb">View Demo</a>
    ·
    <a href="https://github.com/eudesrodrigo/brFinance/issues">Report Bug</a>
    ·
    <a href="https://github.com/eudesrodrigo/brFinance/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

## About The Project

brFinance is a web scraping package to simplify access to financial data. It provides data from various sources such as CVM (brazilian equivelent of SEC), B3 (Brazilian stock exchange), Banco Central (brazilian equivalent of FED), ANBIMA, etc.

Here's is some of the data currently available:
* Financial statements:
* * Balanço Patrimonial Ativo (Balance sheet - Assets)
* * Balanço Patrimonial Passivo (Balance sheet - Liabilities)
* * Demonstração do Resultado  (Income statement)
* * Demonstração do Resultado Abrangente
* * Demonstração do Fluxo de Caixa (Cash flow statement)
* * Demonstração das Mutações do Patrimônio Líquido
* * Demonstração de Valor Adicionado

* Banco central PTAX (average trade price for currencies in BRL)

* ANBIMA IMA index (brazilian bonds index)

### Built With

This package uses mainly:
* [Pandas](https://pandas.pydata.org/)
* [Selenium](https://pypi.org/project/selenium/)
* [Beautifulsoup](https://pypi.org/project/beautifulsoup4/)

<!-- GETTING STARTED -->
## Getting Started

brFinance uses selenium and webdriver to automate page navigation (ChromeDriver, Geckodriver, etc). The package sets up
the driver automaticaly, however you can also set it up on your own.
[Click here](https://selenium-python.readthedocs.io/installation.html) to understand how to setup Selenium webdriver on
your OS.

### Installation

1. Install the package
   ```sh
   pip install git+git://github.com/eudesrodrigo/brFinance
   ```

## Usage

We encourage you to have a look at our ```examples``` folder where you will find a quick explanation on how to use the
library to get the data available.

### Brazilian companies data (Quarter and Anual reports)

This package gets data from the CVM website that is periodically updated.
[![Method to get the CVM codes and company names available.][b3]](https://www.rad.cvm.gov.br/ENETCONSULTA/frmGerenciaPaginaFRE.aspx?NumeroSequencialDocumento=100673&CodigoTipoInstituicao=2)

After importing the package you can create a new Company object by providing the company CVM code:

```python
from brFinance.scraper.cvm.company import Company

# Instantiate object for Petrobras (Cod. CVM = 9512)
petrobras = Company(cvm_code=9512)

# Get useful information about Petrobras
print(petrobras.get_social_capital_data())
print(petrobras.get_registration_data())

# Get annual and quarterly reports separately
annual_reports = petrobras.get_annual_reports()
quarterly_reports = petrobras.get_quarterly_reports()
```

Once you have instatiated the Company object you can access its attributes. The "reports" variable is a list of dicts
with all financial statements available organized by reference date:

```python
# Getting data
print(quarterly_reports["31/03/2021"]["Demonstração do Resultado"])

# Get available dates
print(annual_reports.keys())
print(quarterly_reports.keys())

# Get available report for each date
print(quarterly_reports["31/03/2021"].keys())
```

### CVM codes available

You can also use the method get_cvm_codes() from class SearchDFP or SearchITR to find the CVM code for a specific
company:

```python
from brFinance.scraper.cvm.search import SearchDFP, SearchITR

search_dfp = SearchDFP()  # Demonstração Financeira Padronizada

# Get all CVM codes available
print(search_dfp.get_cvm_codes())
```

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any
contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.


## Contact

Your Name - [@eudesrodrigo](https://twitter.com/eudesrodrigo) - eudesrodrigo@outlook.com

Project Link: [https://github.com/eudesrodrigo/brFinance](https://github.com/eudesrodrigo/brFinance)


## Acknowledgements
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)
* [Img Shields](https://shields.io)
* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Pages](https://pages.github.com)
* [Animate.css](https://daneden.github.io/animate.css)
* [Loaders.css](https://connoratherton.com/loaders)
* [Slick Carousel](https://kenwheeler.github.io/slick)
* [Smooth Scroll](https://github.com/cferdinandi/smooth-scroll)
* [Sticky Kit](http://leafo.net/sticky-kit)
* [JVectorMap](http://jvectormap.com)
* [Font Awesome](https://fontawesome.com)





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/eudesrodrigo/brFinance.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/brFinance/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/eudesrodrigo/brFinance.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/brFinance/network/members
[stars-shield]: https://img.shields.io/github/stars/eudesrodrigo/brFinance.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/brFinance/stargazers
[issues-shield]: https://img.shields.io/github/issues/eudesrodrigo/brFinance.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/brFinance/issues
[license-shield]: https://img.shields.io/github/license/eudesrodrigo/brFinance.svg?style=for-the-badge
[license-url]: https://github.com/eudesrodrigo/brFinance/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/eudesrodrigo
[b3]: images/image-4.png