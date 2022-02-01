[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

# brfinance - Acesse facilmente dados financeiros de empresas brasileiras na B3/CVM
Biblioteca em Python com o objetivo de facilitar o acesso a dados financeiros periódicos de empresas brasileiras(B3/CVM).
* Financial statements:
* * Balanço Patrimonial Ativo (Balance sheet - Assets)
* * Balanço Patrimonial Passivo (Balance sheet - Liabilities)
* * Demonstração do Resultado  (Income statement)
* * Demonstração do Resultado Abrangente
* * Demonstração do Fluxo de Caixa (Cash flow statement)
* * Demonstração das Mutações do Patrimônio Líquido
* * Demonstração de Valor Adicionado

<!-- ![image](https://i.imgur.com/TBpVWm3.png) -->

## Instalação
```
$ pip install brfinance
```

## Como utilizar
Veja como é simples utilizar:
```python
from brfinance import CVMAsyncBackend
import pandas as pd
from datetime import datetime, date


cvm_httpclient = CVMAsyncBackend()

# Dict de códigos CVM para todas as empresas
cvm_codes = cvm_httpclient.get_cvm_codes()
print(cvm_codes)

# Dict de todas as categorias de busca disponíveis (Fato relevante, DFP, ITR, etc.)
categories = cvm_httpclient.get_consulta_externa_cvm_categories()
print(categories)

# Realizando busca por Empresa
start_date = date(2020, 1, 1)
end_dt = date.today()
cvm_codes_list = ['21610'] # B3
category = ["EST_4", "EST_3", "IPE_4_-1_-1"] # Códigos de categoria para DFP, ITR e fatos relevantes
last_ref_date = False # Se "True" retorna apenas o último report no intervalo de datas

# Busca
search_result = cvm_httpclient.get_consulta_externa_cvm_results(
    cod_cvm=cvm_codes_list,
    start_date=start_date,
    end_date=end_dt,
    last_ref_date=last_ref_date,
    category=category
    )

# Filtrar dataframe de busca para DFP e ITR apenas
search_result = search_result[
    (search_result['categoria']=="DFP - Demonstrações Financeiras Padronizadas") |
    (search_result['categoria']=="ITR - Informações Trimestrais")]
search_result = search_result[pd.to_numeric(search_result['numero_seq_documento'], errors='coerce').notnull()]

reports_list = [
    'Balanço Patrimonial Ativo',
    'Balanço Patrimonial Passivo',
    'Demonstração do Resultado',
    'Demonstração do Resultado Abrangente',
    'Demonstração do Fluxo de Caixa',
    'Demonstração das Mutações do Patrimônio Líquido',
    'Demonstração de Valor Adicionado'] # Se None retorna todos os demonstrativos disponíveis.

# Obter demonstrativos
for index, row in search_result.iterrows():
    empresa = f"{row['cod_cvm']} - {cvm_codes[row['cod_cvm']]}"
    print("*" * 20, empresa, "*" * 20)
    reports = cvm_httpclient.get_report(row["numero_seq_documento"], row["codigo_tipo_instituicao"], reports_list=reports_list)
    
    for report in reports:
        reports[report]["cod_cvm"] = row["cod_cvm"]
        print(reports[report].head())
```
Você pode acessar exemplos completos clicando [aqui](https://github.com/eudesrodrigo/brFinance/tree/master/examples).


### Funções disponíveis

Através da classe de client `CVMAsyncBackend`, você terá acesso as seguintes funções:

| Função        |  Parâmetros          | Descrição  |
| ------------- |:-------------:| -----|
| get_cvm_codes      | - | Obtém os códigos cvm disponíveis para todas as empresas. Retorna um dicionário com o código CVM de chave e o nome da empresa. |
| get_consulta_externa_cvm_categories      | - |   Obtém os códigos para as categorias de busca disponíveis, dentre elas "DFP", "ITR", etc. Retorna um dicionário com o código da busca e a descrição. |
| get_consulta_externa_cvm_results | cod_cvm, start_date, end_date, last_ref_date, report_type | Obtém o resultado da busca para os dados informados. Retorna um dataframe com os resultados.|
| get_report | numero_seq_documento, codigo_tipo_instituicao, reports_list, previous_results | Utilizado para obter todos os demonstrativos de uma empresa na CVM. Retorna um dicionário com os nomes e os valores dos demonstrativos em um dataframe. |


### Upload PyPi
```
pip install twine
```
```
python setup.py sdist
```
```
C:\Users\eudes\AppData\Roaming\Python\Python310\Scripts\twine
```
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
