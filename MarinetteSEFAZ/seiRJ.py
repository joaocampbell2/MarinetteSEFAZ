import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import  Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.common.exceptions import TimeoutException


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
    
    WebDriverWait(navegador,8).until(EC.presence_of_element_located, ((By.XPATH, "//div[text() = 'Controle de Processos']")))
    
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
        salvar = navegador.find_element(By.XPATH, '//button[@value = "Salvar"]')
        salvar.click()
        
    except:
       traceback.print_exc()
       navegador.find_element(By.XPATH, "//div[@class = 'sparkling-modal-close']").click()
    finally:
        navegador.switch_to.default_content()
        WebDriverWait(navegador,3).until(EC.invisibility_of_element_located(((By.XPATH, "//div[@class = 'sparkling-modal-overlay']"))))

def buscarInformacaoEmDocumento(navegador,documento, regex, verificador = None,show=False):
    
    navegador.switch_to.default_content()
    WebDriverWait(navegador,20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrArvore")))
    
    documento.click()
    navegador.switch_to.default_content()            
    WebDriverWait(navegador,20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrVisualizacao")))
    WebDriverWait(navegador,20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrArvoreHtml")))


    if verificador == None:
        time.sleep(1)  
        
    else:
        if isinstance(verificador, list):
            condicao = "//*["
            
            for item in verificador:
                condicao += "contains(text(), '" + item + "') or "
            
            condicao = condicao[:-4]
            condicao += "]"    
        else:
            condicao = "//*[contains(text(), '" + verificador + "')]"
        
        
        try:
            WebDriverWait(navegador,3).until(EC.presence_of_element_located((By.XPATH, condicao)))
        except:
            return None
    
    body = navegador.find_element(By.XPATH, '//body').text    
    
    if show:
        print(body)
    
    if isinstance(regex,list):
        resultado = []
        for item in regex:
            resultado.append(re.search(item,body))
        if all(elem is None for elem in resultado):
            return None
    if isinstance(regex,str):
        resultado = re.search(regex,body)
    
    
    navegador.switch_to.default_content()

    return resultado

def incluirProcessoEmBloco(navegador,processo,bloco):
    navegador.switch_to.default_content()
    WebDriverWait(navegador,5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrArvore")))
    navegador.find_element(By.XPATH, "//span[text() = '"+processo+"']").click()
    navegador.switch_to.default_content()
    WebDriverWait(navegador,5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrVisualizacao")))
    WebDriverWait(navegador,5).until(EC.element_to_be_clickable((By.XPATH, "//img[@alt = 'Incluir em Bloco']"))).click()
    navegador.switch_to.default_content()
    WebDriverWait(navegador,5).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@name = 'modal-frame']")))
    WebDriverWait(navegador,5).until(EC.element_to_be_clickable((By.XPATH, "//a[text() = '"+bloco+"']"))).click()
    navegador.switch_to.default_content()  
    try:
        WebDriverWait(navegador,2).until(EC.alert_is_present())
        navegador.switch_to.alert.accept()
        raise Exception("Processo já incluso no bloco")
    except TimeoutException:
        print("Processo adicionado no bloco " + bloco)
    except:
        raise
    
    
def removerProcessoDoBloco(navegador:  webdriver.Firefox,nProcesso):
    processos = navegador.find_elements(By.XPATH, "//tbody//tr")
    for processo in processos:
        if nProcesso in processo.text:
            processo.find_element(By.XPATH,".//td//a//img[@title='Retirar Processo/Documento do Bloco']").click()
            break 
        
    WebDriverWait(navegador,5).until(EC.alert_is_present())
    navegador.switch_to.alert.accept()
    navegador.switch_to.default_content()
    print("Processo removido do bloco")

def buscarProcessoEmBloco(navegador,n):
    WebDriverWait(navegador,20).until(EC.invisibility_of_element_located(((By.XPATH, "//div[@class = 'sparkling-modal-close']"))))
    WebDriverWait(navegador,20).until(EC.presence_of_element_located(((By.XPATH, "//tbody//tr"))))
    processo = navegador.find_elements(By.XPATH, "//tbody//tr")[n]
    nProcesso = processo.find_element(By.XPATH, './/td[3]//a')
    return nProcesso

def incluirDocumento(navegador: webdriver.Firefox,tipoDocumento,textoInicial=None,modelo=None,acesso = "Restrito", hipotese= "Controle Interno (Art. 26, § 3º, da Lei nº 10.180/2001)"):
    navegador.switch_to.default_content()
    WebDriverWait(navegador,5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrVisualizacao")))
    WebDriverWait(navegador,5).until(EC.element_to_be_clickable((By.XPATH, "//img[@alt = 'Incluir Documento']"))).click()
    WebDriverWait(navegador,5).until(EC.presence_of_element_located((By.XPATH,"//label[text() = 'Escolha o Tipo do Documento: ']")))
    navegador.find_element(By.XPATH,'//a[text() = "' + tipoDocumento +'"]').click()
    
    inicial = {"Documento Modelo": "ProtocoloDocumentoTextoBase", "Texto Padrão": "TextoPadrao", "Nenhum" : None, None : None}
    textoInicial = inicial.get(textoInicial,textoInicial)
    
    
    WebDriverWait(navegador, 5).until(EC.element_to_be_clickable((By.ID, "divOptProtocoloDocumentoTextoBase")))

    
    if textoInicial:
        navegador.find_element(By.XPATH, "//label[@for = 'opt" + textoInicial + "']").click()
        input = WebDriverWait(navegador,5).until(EC.presence_of_element_located((By.XPATH,"//input[@id= 'txt" + textoInicial + "']")))
        input.send_keys(modelo)
        time.sleep(1)
        input.send_keys(Keys.ENTER)
    
    
    controleAcesso = {"Sigiloso" : "optSigiloso", "Restrito" : "optRestrito", "Público": "optPublico"}
    
    acesso = controleAcesso.get(acesso,acesso)
    
    navegador.find_element(By.XPATH,'//label[@for ="' + acesso + '"]').click()
    if acesso != "optPublico":
        hipoteses = Select(navegador.find_element(By.ID, 'selHipoteseLegal'))
        hipoteses.select_by_visible_text(hipotese)
    
    
    navegador.find_element(By.XPATH, "//button[@name = 'btnSalvar']").click()
    
    
    
def inserirHyperlinkSEI(nav:  webdriver.Firefox,nDocumento):
    nav.switch_to.default_content()
    nav.find_element(By.XPATH, "//a[@id = 'cke_178']").click()
    nav.find_element(By.XPATH, "//input[@class = 'cke_dialog_ui_input_text']").send_keys(nDocumento)
    nav.find_element(By.XPATH, "//a[@class = 'cke_dialog_ui_button cke_dialog_ui_button_ok']").click()
    
    #FAZER TRATAMENTO DE ERROS
    
    
def limparAnotacao(nav:  webdriver.Firefox,nProcesso):
    processos = nav.find_elements(By.XPATH, "//tbody//tr")
    for processo in processos:
        if nProcesso in processo.text:
            processo.find_element(By.XPATH,".//td//a//img[@title='Anotações']").click()
            break                       
    try:
        WebDriverWait(nav,5).until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, 'iframe')))

        txtarea = nav.find_element(By.XPATH, '//textarea[@id = "txtAnotacao"]')
        txtarea.send_keys(Keys.CONTROL + "a")
        txtarea.send_keys(Keys.BACKSPACE)

        salvar = nav.find_element(By.XPATH, '//button[@value = "Salvar"]')
        salvar.click()
        
    except:
       traceback.print_exc()
       nav.find_element(By.XPATH, "//div[@class = 'sparkling-modal-close']").click()
    finally:
        nav.switch_to.default_content()
        WebDriverWait(nav,3).until(EC.invisibility_of_element_located(((By.XPATH, "//div[@class = 'sparkling-modal-overlay']"))))
        
def escreverAcompanhamentoEspecial(nav: webdriver.Firefox,processo, texto,grupoAcompanhamento):

    nav.switch_to.default_content()
    WebDriverWait(nav,5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrArvore")))
    nav.find_element(By.XPATH, "//span[text() = '"+processo+"']").click()
    nav.switch_to.default_content()
    WebDriverWait(nav,5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrVisualizacao")))
    
    WebDriverWait(nav,5).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Processo aberto')]")))
    nav.find_element(By.XPATH, "//img[@title = 'Acompanhamento Especial']").click()

    try:
        WebDriverWait(nav,2).until(EC.presence_of_element_located((By.XPATH, '//img[@alt ="Alterar Acompanhamento"]'))).click()
    except:
        try:
            WebDriverWait(nav,2).until(EC.presence_of_element_located((By.XPATH, '//img[@alt ="Novo Grupo de Acompanhamento"]')))
        except:
            raise Exception("Acompanhamento não encontrado")             
    
    WebDriverWait(nav,10).until(EC.presence_of_element_located((By.ID, "selGrupoAcompanhamento")))
    selGrupoAcompanhamento = Select(nav.find_element(By.ID, "selGrupoAcompanhamento"))
    selGrupoAcompanhamento.select_by_visible_text(grupoAcompanhamento)
    
    caixaDeTexto = nav.find_element(By.ID, "txaObservacao")
    caixaDeTexto.send_keys(Keys.PAGE_DOWN)
    caixaDeTexto.send_keys(Keys.END)

    textoOriginal = nav.find_element(By.XPATH, "//textarea").text

    for info in texto:
        if info.upper() not in textoOriginal.upper():  
            info = "\n" + info + " /"    
            if len(textoOriginal) + len(info) > 500:
                raise Exception("Texto cheio!")
            
            caixaDeTexto.send_keys(info)
            print('"'+info + '" adicionada!')
            textoOriginal += info
    nav.find_element(By.XPATH, "//button[@value = 'Salvar']").click()
    nav.switch_to.default_content()
    
    
def buscarNumeroDocumento(nav: webdriver.Firefox,documento):
    nav.switch_to.default_content()

    WebDriverWait(nav,20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ifrArvore")))
    abrirPastas(nav)

    docs = nav.find_elements(By.XPATH, "//div[@id = 'divArvore']//div//a[@class = 'infraArvoreNo']")
        
    for doc in reversed(docs):
        texto = doc.text
        if documento in texto:
            nav.switch_to.default_content()
            return  re.search(r"(\d+)\)?$", texto).group(1)



def incluirEmBlocoDeAssinatura(nav,blocoAssinatura, documento = None):
    print("Incluindo no novo bloco de assinatura...")
    nav.switch_to.default_content()

    iframeBotoes = nav.find_element(By.ID, "ifrVisualizacao")
    nav.switch_to.frame(iframeBotoes)

    arvoreBotoes = nav.find_element(By.ID, "divInfraAreaTela")
    botoesSei = arvoreBotoes.find_element(By.CLASS_NAME, "barraBotoesSEI")
    opcoesBotoesSei = botoesSei.find_elements(By.TAG_NAME, "a")
    for opcaoBotaoSei in opcoesBotoesSei:
        infoBotao = opcaoBotaoSei.find_element(By.TAG_NAME, "img")
        attrTitle = infoBotao.get_attribute("title")
        if attrTitle == "Incluir em Bloco de Assinatura":
            opcaoBotaoSei.click()
            break

    WebDriverWait(nav, 20).until(EC.element_to_be_clickable((By.ID, "selBloco")))
    # Clicar para abrir a aba de blocos
    nav.find_element(By.ID, "selBloco").click()
    selecaoBloco = nav.find_element(By.ID, "selBloco")
    optionsBloco = selecaoBloco.find_elements(By.TAG_NAME, "option")
   

    for optionBloco in optionsBloco:
        if optionBloco.text == blocoAssinatura:
            optionBloco.click()
            break
            
    
    # Incluir no bloco de assinatura
    nav.find_element(By.ID, "sbmIncluir").click()

    nav.switch_to.default_content()

    print("Incluido com sucesso.")
    