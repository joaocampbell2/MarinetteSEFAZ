import time
from time import sleep
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import  Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re
from openpyxl import load_workbook
from datetime import date
from glob import glob
from shutil import move
import tabula
from PyPDF2 import PdfReader

def loginSEI(navegador: webdriver.Firefox, login, senha,nomeCoordenacao):
    
    navegador.get("https://sei.rj.gov.br/sip/login.php?sigla_orgao_sistema=ERJ&sigla_sistema=SEI")
    
    usuario = navegador.find_element(By.XPATH, value='//*[@id="txtUsuario"]')
    usuario.send_keys(login)

    senha = navegador.find_element(By.XPATH, value='//*[@id="pwdSenha"]')
    senha.send_keys(senha)

    exercicio = Select(navegador.find_element(By.XPATH, value='//*[@id="selOrgao"]'))
    exercicio.select_by_visible_text('SEFAZ')

    btnLogin = navegador.find_element(By.XPATH, value='//*[@id="Acessar"]')
    btnLogin.click()

    navegador.maximize_window()
    
    WebDriverWait(navegador,5).until(EC.presence_of_element_located, ((By.XPATH, "//div[text() = 'Controle de Processos']")))
    
    navegador.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE) 
    
    trocarCoordenacao(navegador, nomeCoordenacao)
    
    
def trocarCoordenacao(navegador: webdriver.Firefox, nomeCoordenacao):
    coordenacao = navegador.find_elements(By.XPATH, "//a[@id = 'lnkInfraUnidade']")[1]
    print(coordenacao)
    if coordenacao.get_attribute("innerHTML") != nomeCoordenacao:
        print(coordenacao)
        coordenacao.click()
        WebDriverWait(navegador,5).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Trocar Unidade')]")))
        navegador.find_element(By.XPATH, "//td[text() = '"+nomeCoordenacao+"' ]").click() 
        
def abrirPastas(navegador: webdriver.Firefox):
    navegador.switch_to.default_content()
    WebDriverWait(navegador,20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrArvore")))
    listaDocs = WebDriverWait(navegador,5).until(EC.presence_of_element_located((By.ID, "divArvore")))
    pastas = listaDocs.find_elements(By.XPATH, '//a[contains(@id, "joinPASTA")]')
    
    for doc in pastas[:-1]:
        doc.click() 
        WebDriverWait(navegador,5).until(EC.presence_of_element_located((By.XPATH, "//*[text() = 'Aguarde...']")))
        WebDriverWait(navegador,5).until(EC.invisibility_of_element((By.XPATH, "//*[text() = 'Aguarde...']")))
    
    navegador.switch_to.default_content()
    
def pesquisarProcesso(navegador: webdriver.Firefox, processoSEI):

    barraPesquisa = navegador.find_element(By.ID, "txtPesquisaRapida")
    barraPesquisa.send_keys(processoSEI)
    barraPesquisa.send_keys(Keys.ENTER)