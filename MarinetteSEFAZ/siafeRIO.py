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


def loginSIAFE(navegador: webdriver.Firefox, login, senha_siafe):
    navegador.get("https://siafe2.fazenda.rj.gov.br/Siafe/faces/login.jsp")

    usuario = navegador.find_element(By.XPATH, value='//*[@id="loginBox:itxUsuario::content"]')
    usuario.send_keys(login)

    senha = navegador.find_element(By.XPATH, value='//*[@id="loginBox:itxSenhaAtual::content"]')
    senha.send_keys(senha_siafe)
    
    btnLogin = navegador.find_element(By.XPATH, value='//*[@id="loginBox:btnConfirmar"]')
    btnLogin.click()

    try:
        WebDriverWait(navegador,2).until(EC.element_to_be_clickable((By.XPATH, "//a[@class = 'x12k']"))).click()        
    except:
        pass

    navegador.maximize_window()