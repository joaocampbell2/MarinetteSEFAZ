import time
from time import sleep
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import  Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


def loginSEI(navegador: webdriver.Firefox, login, senha,nomeCoordenacao):
    
    navegador.get("https://sei.rj.gov.br/sip/login.php?sigla_orgao_sistema=ERJ&sigla_sistema=SEI")
    
    usuario = navegador.find_element(By.XPATH, value='//*[@id="txtUsuario"]')
    usuario.send_keys(login)

    campoSenha = navegador.find_element(By.XPATH, value='//*[@id="pwdSenha"]')
    campoSenha.send_keys(senha)

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
    if coordenacao.get_attribute("innerHTML") != nomeCoordenacao:
        coordenacao.click()
        WebDriverWait(navegador,5).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Trocar Unidade')]")))
        navegador.find_element(By.XPATH, "//td[text() = '"+nomeCoordenacao+"' ]").click() 
        
def abrirPastas(navegador: webdriver.Firefox):
    navegador.switch_to.default_content()
    WebDriverWait(navegador,20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrArvore")))
    listaDocs = WebDriverWait(navegador,5).until(EC.presence_of_element_located((By.ID, "divArvore")))
    pastas = listaDocs.find_elements(By.XPATH, '//a[contains(@id, "joinPASTA")]//img[contains(@title, "Abrir")]')
    
    for doc in pastas:
        doc.click() 
        WebDriverWait(navegador,5).until(EC.presence_of_element_located((By.XPATH, "//*[text() = 'Aguarde...']")))
        WebDriverWait(navegador,5).until(EC.invisibility_of_element((By.XPATH, "//*[text() = 'Aguarde...']")))
        
def pesquisarProcesso(navegador: webdriver.Firefox, processoSEI):

    barraPesquisa = navegador.find_element(By.ID, "txtPesquisaRapida")
    barraPesquisa.send_keys(processoSEI)
    barraPesquisa.send_keys(Keys.ENTER)
    
    WebDriverWait(navegador,10).until(EC.presence_of_element_located((By.ID, "ifrArvore")))    

    
def procurarArquivos(navegador: webdriver.Firefox, listaArquivos):
    listaArquivos = transformarElementoEmLista(listaArquivos)


    lista = []
    navegador.switch_to.default_content()

    arvore = WebDriverWait(navegador,10).until(EC.presence_of_element_located((By.ID, "ifrArvore")))    
    navegador.switch_to.frame(arvore)
    abrirPastas(navegador)

    docs = navegador.find_elements(By.XPATH, "//div[@id = 'divArvore']//div//a[@class = 'infraArvoreNo']")
    quantDocs = len(docs)
    
    
    for doc in (range(quantDocs)):
        docTexto = docs[doc].text
        if any(arquivo.upper() in docTexto.upper() for arquivo in listaArquivos):   
            lista.append(docs[doc])
    
    navegador.switch_to.default_content()
                
    return lista      
    
def baixarArquivos(navegador: webdriver.Firefox, listaArquivos):
    
    listaArquivos = transformarElementoEmLista(listaArquivos)

    navegador.switch_to.default_content()
    
    arvore = WebDriverWait(navegador,10).until(EC.presence_of_element_located((By.ID, "ifrArvore")))    
    navegador.switch_to.frame(arvore)
    
    abrirPastas(navegador)

    listaDocs =  WebDriverWait(navegador,10).until(EC.presence_of_element_located((By.ID, "divArvore")))  
    docs = listaDocs.find_elements(By.TAG_NAME, "a")
    
    for doc in docs:
        if any(arquivo.upper() in doc.text.upper() for arquivo in listaArquivos):
            doc.click()
            

def transformarElementoEmLista(listaArquivos):
    if isinstance(listaArquivos,str):
        arquivo = listaArquivos
        listaArquivos = []
        listaArquivos.append(arquivo)
        return listaArquivos
    else:
        return listaArquivos
    
def acessarBloco(navegador, blocoSolicitado):
    navegador.find_element(By.XPATH, "//span[text() = 'Blocos']").click()
    WebDriverWait(navegador,10).until(EC.element_to_be_clickable((By.XPATH, "//span[text() = 'Internos']"))).click()
    blocos = navegador.find_elements(By.XPATH, "//tbody//tr")[1:-1]

    for bloco in blocos:    
        nBloco = bloco.find_elements(By.XPATH,".//td")[1]
        if nBloco.text == blocoSolicitado:
            nBloco.find_element(By.XPATH, './/a').click()
            break     
    else:
        raise Exception("Bloco não encontrado")
        
def obterProcessosDeBloco(navegador,blocoSolicitado):
    navegador.find_element(By.XPATH, "//span[text() = 'Blocos']").click()
    WebDriverWait(navegador,10).until(EC.element_to_be_clickable((By.XPATH, "//span[text() = 'Internos']"))).click()
    blocos = navegador.find_elements(By.XPATH, "//tbody//tr")[1:-1]

    for bloco in blocos:    
        nBloco = bloco.find_elements(By.XPATH,".//td")[1]
        if nBloco.text == blocoSolicitado:
            nBloco.find_element(By.XPATH, './/a').click()
            break
    else:
        raise Exception("Bloco não encontrado")
  
    processos = navegador.find_elements(By.XPATH, "//tbody//tr")
    return processos
  
def escreverAnotacao(navegador,texto,nProcesso):
    processos = navegador.find_elements(By.XPATH, "//tbody//tr")
    for processo in processos:
        if nProcesso in processo.text:
            processo.find_element(By.XPATH,".//td//a//img[@title='Anotações']").click()
            break                       
    try:
        WebDriverWait(navegador,5).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, 'iframe')))

        txtarea = navegador.find_element(By.XPATH, '//textarea[@id = "txtAnotacao"]')

        txtarea.send_keys(Keys.PAGE_DOWN)
        txtarea.send_keys(Keys.END)
        for paragrafo in texto:
            txtarea.send_keys(Keys.ENTER)
            txtarea.send_keys(paragrafo)
        time.sleep(1)
        salvar = navegador.find_element(By.XPATH, '//button[@value = "Salvar"]')
        salvar.click()
        
    except:
       traceback.print_exc()
       time.sleep(1)
       navegador.find_element(By.XPATH, "//div[@class = 'sparkling-modal-close']").click()
    finally:
        navegador.switch_to.default_content()
        
def buscarInformacaoEmDocumento(navegador,documento, regex, verificador = None):
    
    navegador.switch_to.default_content()
    WebDriverWait(navegador,20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrArvore")))
    
    documento.click()
    navegador.switch_to.default_content()            
    WebDriverWait(navegador,20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrVisualizacao")))
    WebDriverWait(navegador,20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrArvoreHtml")))

    if verificador == None:
        time.sleep(1)
    else:
        try:
            WebDriverWait(navegador,2).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '" + verificador + "')]")))
        except:
            print("VERIFICADOR NÃO ENCONTRADO")
            return None
    
    body = navegador.find_element(By.XPATH, '//body').text
    
    if isinstance(regex,list):
        resultado = []
        for item in regex:
            resultado.append(re.search(item,body))
    if isinstance(regex,str):
        resultado = re.search(regex,body)
    
    
    navegador.switch_to.default_content()

    return resultado

