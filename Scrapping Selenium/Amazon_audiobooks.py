import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import time

# Descomentar para executar em headless mode:
# Headless >> Sem visualizar na máquina!

#options = Options()  # Initialize an instance of the Options class
#options.headless = True  # True -> Headless mode activated
#options.add_argument('window-size=1920x1080')  # Set a big window size, so all the data will be displayed

web = "https://www.audible.com/search"
path = 'C:/Web Scrapping/chromedriver-win64/chromedriver.exe'

driver = webdriver.Chrome(path, options=options)  # add the "options" argument to make sure the changes are applied
driver.get(web)

# Paginação:
elem_paginas = driver.find_element_by_xpath('.//ul[contains(@class, "pagingElements")]')
paginas = elem_paginas.find_elements_by_tag_name('li')
ult_pag = int(paginas[-2].text) 

#Inicializando listas p/ armazenar resultados:
titulo = []
autor  = []
tamanho= []

pag = 1 # Primeira página
while pag <= ult_pag:
    time.sleep(8)
    
    container = driver.find_element_by_class_name('adbl-impression-container ')
    livros = container.find_elements_by_xpath('.//li[contains(@class, "productListItem")]')


    for livro in livros:
        titulo.append(
            livro.find_element_by_xpath('.//h3[contains(@class, "bc-heading")]').text
        )

        autor.append(
            livro.find_element_by_xpath('.//li[contains(@class, "authorLabel")]').text
        )

        tamanho.append(
            livro.find_element_by_xpath('.//li[contains(@class, "runtimeLabel")]').text
        )

    #Incrementando pagina:
    pag += 1
    
    # Acessando preoxima pagina:
    try:
        nova_pag = driver.find_element_by_xpath('.//span[contains(@class , "nextButton")]')
        nova_pag.click()
    except:
        pass

# Fechando driver:
driver.quit()

df_livros = pd.DataFrame({'titulo': titulo, 'Autor': autor, 'Tamanho': tamanho})
df_livros.to_csv('amazon_audiobooks.csv', index=False)

