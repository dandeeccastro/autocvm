import os
import unidecode
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

initialURL = "https://cvmweb.cvm.gov.br/SWB/Sistemas/SCW/CPublica/CiaAb/FormBuscaCiaAb.aspx?TipoConsult=c"

dictionary = {
    "ata": "ATA",
    "boletim de voto a distancia":"BVD",
    "mapa consolidado de voto a distancia":"MPBVD",
    "mapa de depositario central":"MPDC",
    "mapa do escriturador":"MPESC",
    "mapa final de votacao":"MPFIN",
    "mapa final de votacao detalhado":"MPFDET",
    "mapa final de votacao sintetico":"MPFSIN",
    "material referente a pedidos publicos de procuracao":"PPP",
    "proposta da administracao":"PROPAD",
    "sumario das decisoes":"SUM"
}

options = Options()
options.add_experimental_option("prefs", {
  "download.default_directory": "/home/dandee/Documents/Projetos/DoutoradoAutomatizacao/out",
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True
})

chromium = webdriver.Chrome(options=options)
wait = WebDriverWait(chromium,50)

validTypes = ["AGO","AGO/E","AGE"]
invalidSpecimens = ["manual para participacao","justificacao de incorporacao, fusao ou cisao","protocolo de incorporacao, fusao ou cisao","protocolo e justificativa de incorporacao, fusao ou cisao","protocolo e justificacao de incorporacao, fusao ou cisao","edital de convocacao"]

downloadedFiles = []

def TableRowDataToFileName(companyCode,docType,specimenCode,date,status,version,category):
    companyCode = ''.join(companyCode.split('-'))

    docType = ''.join(docType.split('/'))
    try:
        specimenCode = dictionary[unidecode.unidecode(specimenCode.lower())]
    except KeyError:
        print ("|"+unidecode.unidecode(specimenCode.lower())+"|")
        specimenCode = "ERROR"

    dateArr = date.split()
    dateArr[0] = dateArr[0].split('/')[::-1]

    if (len(dateArr[0][0]) is 2):
        dateArr[0][0] = "20" + dateArr[0][0]
    if (len(dateArr[0][1]) is 1):
        dateArr[0][1] = '0' + dateArr[0][1]
    if (len(dateArr[0][2]) is 1):
        dateArr[0][2] = '0' + dateArr[0][2]

    dateArr[0] = ''.join(dateArr[0])
    dateArr[1] = ''.join(dateArr[1].split(':'))
    date = ''.join(dateArr)

    status = status[0]

    finalIterable = (companyCode,docType,specimenCode,date,status,version,category)

    return '_'.join(finalIterable)
def queryCVM():

    # Parte onde temos o formulario para a empresa escolhida
    wait.until(EC.invisibility_of_element_located((By.ID,"divLoading")))
    # wait.until(EC.presence_of_element_located((By.ID, "rdPeriodo")))
    wait.until(EC.invisibility_of_element_located((By.ID,"divSplash")))

    periodRadio = chromium.find_element_by_id("rdPeriodo")
    periodRadio.click()

    wait.until(EC.visibility_of_element_located((By.ID, "txtDataIni")))

    txtDataIni = chromium.find_element_by_id("txtDataIni")
    txtDataIni.send_keys("05/01/2017")
    txtHoraIni = chromium.find_element_by_id("txtHoraIni")
    txtHoraIni.send_keys("00:00")

    cboCategoria = chromium.find_elements_by_tag_name("select")[0]
    try:
        Select(cboCategoria).select_by_visible_text("Assembleia")
    except NoSuchElementException:
        return 0

    wait.until(EC.invisibility_of_element_located((By.ID,"divSplash")))
    btnConsulta = chromium.find_element_by_id("btnConsulta")
    btnConsulta.click()
    wait.until(EC.invisibility_of_element_located((By.ID,"divSplash")))
    return 1

def fillCompanyName(companyID):

    chromium.get(initialURL)
    inputField = chromium.find_element_by_id("txtCNPJNome")
    inputField.send_keys(companyID)
    # inputField.send_keys(Keys.ENTER)

def findFirstValidCompany():
    wait.until_not(EC.presence_of_element_located((By.ID,"txtCNPJNome")))
    try:
        if (EC.presence_of_element_located((By.ID, "lblMsg"))):
            possibleError = chromium.find_element_by_id("lblMsg")
            if "Nenhuma companhia foi encontrada com o critério de busca especificado" in possibleError.text:
                return 0
    except NoSuchElementException:
        print("Regular")
    except StaleElementReferenceException:
        print('Regular')
    wait.until(EC.presence_of_element_located((By.ID, "dlCiasCdCVM")))
    # Parte onde temos a tabela de empresas possíveis
    tableRows = chromium.find_elements_by_tag_name("tr")
    found = 0
    for row in tableRows:
        col = row.find_elements_by_tag_name("td")
        if "Concedido" in col[4].text:
            col[4].find_element_by_tag_name("a").click()
            found = 1
            break
    if (not found):
        return 0
    return 1

def DownloadFilesFromResultTable():
    paginationText = chromium.find_element_by_id("grdDocumentos_info")
    text = paginationText.text.split()
    numString = text[len(text) - 2]
    num = int( int(numString) / 100 ) + 1
    for i in range(0,num):
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME,"fi-download")))
        resultRows = chromium.find_elements_by_tag_name("tr")
        GetValidDocs(resultRows)
        nextButton = chromium.find_element_by_id("grdDocumentos_next")
        if ("disabled" not in nextButton.get_attribute("class")):
            nextButton.click()

def GetValidDocs(resultRows):
    oki = 0
    notOki = 0
    for row in resultRows:
        if (len(row.find_elements_by_tag_name("td")) < 10):
            continue
        rowData = row.find_elements_by_tag_name("td")
        if (rowData[3].text in validTypes):
            if (unidecode.unidecode(rowData[4].text.lower()) not in invalidSpecimens):
                if ("Ativo" in rowData[7].text ):
                    oki += 1
                    filename = TableRowDataToFileName(rowData[0].text,rowData[3].text,rowData[4].text,rowData[6].text,rowData[7].text,rowData[8].text,rowData[9].text)
                    downloadedFiles.append(filename)
                    fileLink = row.find_element_by_class_name('fi-download')
                    fileLink.click()
            else:
                notOki += 1
        else:
            notOki += 1

def DownloadDocumentsByCompanyName(companyID):
    fillCompanyName(companyID)
    if (not findFirstValidCompany()):
        return 0
    if (not queryCVM()):
        return 0
    DownloadFilesFromResultTable()
    return 1

def fileLen(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def ChangeDownloadFileName():
    files = filter(os.path.isfile, os.listdir())
    files = [os.path.join('./', f) for f in files] # add path to each file
    files.sort(key=lambda x: os.path.getmtime(x))
    i = 0
    for file in files:
        os.rename(file,downloadedFiles[i])
        i+=1

# def ChangeDownloadFileName(name):
#     for arq in os.listdir():
#         if (arq not in downloadedFiles and "Unconfirmed" not in arq):
#             # Encontrei o arquivo que precisa ser mudado
#             while not os.path.exists(arq):
#                 time.sleep(1)
# 
#             if os.path.isfile(arq):
#                 os.rename(arq,name)
#                 break

def main():
    companyFile = open("updated.csv","r")
    size = fileLen("./updated.csv")
    os.chdir('./out')
    i = 0
    for company in companyFile:
        i += 1
        print( str( (i/size)*100 ) + "%")
        print ("CNPJ: "+ company)
        if DownloadDocumentsByCompanyName(company):
            print("Resultados encontrados")
        else:
            print("Não foram encontrados resultados")
    ChangeDownloadFileName()

main()
