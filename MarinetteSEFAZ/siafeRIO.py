import time
from time import sleep
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import  Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def loginSIAFE(nav: webdriver.Firefox, login, senha_siafe):
    nav.get("https://siafe2.fazenda.rj.gov.br/Siafe/faces/login.jsp")

    usuario = nav.find_element(By.XPATH, value='//*[@id="loginBox:itxUsuario::content"]')
    usuario.send_keys(login)

    senha = nav.find_element(By.XPATH, value='//*[@id="loginBox:itxSenhaAtual::content"]')
    senha.send_keys(senha_siafe)
    
    btnLogin = nav.find_element(By.XPATH, value='//*[@id="loginBox:btnConfirmar"]')
    btnLogin.click()

    try:
        WebDriverWait(nav,2).until(EC.element_to_be_clickable((By.XPATH, "//a[@class = 'x12k']"))).click()        
    except:
        pass

    nav.maximize_window()
    
    popUp(nav)
    
def popUp(nav):
    try:
        WebDriverWait(nav, 2).until(EC.element_to_be_clickable((By.XPATH,
        '//*[@id="pt1:warnMessageDec:newWarnMessagePopup::content"]//*[@id="pt1:warnMessageDec:frmExec:btnNewWarnMessageOK"]'))).click()
    except:
        None