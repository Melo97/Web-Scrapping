import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from time import sleep
from sqlalchemy import create_engine
import psycopg2

def coletor(keyword = "A", pags = None):
    #Setup
    load_dotenv()
    options = Options()
    webdriver_path = os.getenv('WEBDRIVER')
    web = os.getenv('LINK')

    options.headless = True 
    service = Service(webdriver_path)
    driver = webdriver.Chrome(service=service, options = options)

    
    driver.maximize_window()

    # Navegando
    driver.get(web)
    espera = WebDriverWait(driver, 10)
    naveg = espera.until(
        EC.presence_of_element_located((By.ID, "eac-combobox"))
    )

    pesquisa = naveg.find_element(By.NAME, "keywords")
    pesquisa.send_keys(keyword, Keys.RETURN)


    # Paginação:

    elem_paginas =  WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(( By.XPATH, './/ul[contains(@class, "pagingElements")]'))
    )

    paginas = elem_paginas.find_elements(By.TAG_NAME , 'li')
    ult_pag = int(paginas[-2].text) 

    #Inicializando listas p/ armazenar resultados:
    titulo = []
    autor  = []
    tamanho= []

    pag = 1 # Primeira página
    ult_pag = ult_pag if pags == None else pags

    while pag <= ult_pag:
        sleep(np.random.randint(3, 10) )
        
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'adbl-impression-container'))
        )

        livros = container.find_elements(By.XPATH, './/li[contains(@class, "productListItem")]')


        for livro in livros:
            titulo.append(
                livro.find_element(By.XPATH, './/h3[contains(@class, "bc-heading")]').text
            )

            autor.append(
                livro.find_element(By.XPATH, './/li[contains(@class, "authorLabel")]').text
            )

            tamanho.append(
                livro.find_element(By.XPATH, './/li[contains(@class, "runtimeLabel")]').text
            )

        #Incrementando pagina:
        pag += 1
        
        # Acessando preoxima pagina:
        try:
            next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(@class , "nextButton")]'))
            )
            next_btn.click()

        except:
            pass

    # Fechando driver:
    driver.quit()

    df_livros = pd.DataFrame({'titulo': titulo, 'Autor': autor, 'Tamanho': tamanho})
    return df_livros

def create_connection():
    load_dotenv()

    # Configurando Postgres:
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")

    # Cria o engine do SQLAlchemy para o PostgreSQL
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(DATABASE_URL) 

    """Cria uma conexão com o banco de dados PostgreSQL."""
    conn = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
    return conn, engine

def setup_database(conn):
    """Cria a tabela de preços se ela não existir."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            titulo TEXT,
            Autor TEXT,
            Tamanho TEXT
        )
    ''')
    conn.commit()
    cursor.close()

def subir_dados(data, engine, table_name='livros'):
    """Salva uma linha de dados no banco de dados PostgreSQL usando pandas e SQLAlchemy."""
    # Usa SQLAlchemy para salvar os dados no PostgreSQL
    data.to_sql(table_name, engine, if_exists='append', index=False)

def main():
    conn, engine = create_connection()
    setup_database(conn)

    try:
        # Faz a requisição e parseia a página
        dataframe = coletor(keyword = "D",  pags = 4)
        
        # Salva os dados no banco de dados PostgreSQL
        subir_dados(dataframe, engine)
        print("Dados salvos no banco:", dataframe)
            

    except Exception as e:
        print("Parando a execução por...", e)
    finally:
        conn.close()


if __name__ == '__main__':
   main()

    
