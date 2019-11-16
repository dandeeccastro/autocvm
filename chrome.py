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

# profile.set_preference('browser.download.dir', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'))
options = Options()
options.add_experimental_option("prefs", {
  "download.default_directory": r"C:\Users\xxx\downloads\Test",
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True
})

chromium = webdriver.Chrome(chrome_options=options)
wait = WebDriverWait(chromium,100)

validTypes = ["AGO","AGO/E","AGE"]
invalidSpecimens = ["manual para participacao","justificacao de incorporacao, fusao ou cisao","protocolo de incorporacao, fusao ou cisao","protocolo de justificativa de incorporacao, fusao ou cisao","edital de convocacao"]

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
    print(dateArr[0])
    dateArr[1] = ''.join(dateArr[1].split(':'))
    date = ''.join(dateArr)

    status = status[0]

    finalIterable = (companyCode,docType,specimenCode,date,status,version,category)

    return '_'.join(finalIterable)
def queryCVM():

    # Parte onde temos o formulario para a empresa escolhida
    wait.until(EC.invisibility_of_element_located((By.ID,"divLoading")))
    wait.until(EC.presence_of_element_located((By.ID, "rdPeriodo")))
    wait.until(EC.invisibility_of_element_located((By.ID,"divSplash")))

    periodRadio = chromium.find_element_by_id("rdPeriodo")
    periodRadio.click()

    txtDataIni = chromium.find_element_by_id("txtDataIni")
    txtDataIni.send_keys("05/01/2017")
    txtHoraIni = chromium.find_element_by_id("txtHoraIni")
    txtHoraIni.send_keys("00:00")
    txtDataFim = chromium.find_element_by_id("txtDataFim")
    txtDataFim.send_keys("05/01/2019")
    txtHoraFim = chromium.find_element_by_id("txtHoraFim")
    txtHoraFim.send_keys("23:59")

    cboCategoria = chromium.find_elements_by_tag_name("select")[0]
    Select(cboCategoria).select_by_visible_text("Assembleia")

    wait.until(EC.invisibility_of_element_located((By.ID,"divSplash")))
    btnConsulta = chromium.find_element_by_id("btnConsulta")
    btnConsulta.click()
    wait.until(EC.invisibility_of_element_located((By.ID,"divSplash")))

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
    print("Max de arquivos: " + numString)
    num = int( int(numString) / 100 ) + 1
    print ("Fora do Loop de range")
    for i in range(0,num):
        print("Dentro do Loop de Range, Fora do de rows")
        wait.until(EC.presence_of_element_located((By.TAG_NAME,"td")))
        resultRows = chromium.find_elements_by_tag_name("tr")
        print("Rows: " + str(len(resultRows)))
        GetValidDocs(resultRows)
        print ("Saiu do loop de rows")
        nextButton = chromium.find_element_by_id("grdDocumentos_next")
        if ("disabled" not in nextButton.get_attribute("class")):
            nextButton.click()
    print("Saiu do loop de range")

def GetValidDocs(resultRows):
    oki = 0
    notOki = 0
    for row in resultRows:
        print("Dentro do loop de rows")
        print(len(row.find_elements_by_tag_name("td")))
        if (not len(row.find_elements_by_tag_name("td"))):
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
                    ChangeDownloadFileName(filename)

            else:
                notOki += 1
        else:
            notOki += 1
    print("Válidos: " + str(oki) + " | Inválidos: " + str(notOki))

def DownloadDocumentsByCompanyName(companyID):
    fillCompanyName(companyID)
    if (not findFirstValidCompany()):
        return 0
    queryCVM()
    DownloadFilesFromResultTable()
    return 1

def ChangeDownloadFileName(name):
    for arq in os.listdir():
        if (arq not in downloadedFiles):
            # Encontrei o arquivo que precisa ser mudado
            while not os.path.exists(arq):
                time.sleep(1)

            if os.path.isfile(arq):
                os.rename(arq,name)
            os.rename(arq,name)
            break

def main():
    companyFile = open("updated.csv","r")
    os.chdir('./Downloads')
    for company in companyFile:
        print ("CNPJ: "+ company)
        if DownloadDocumentsByCompanyName(company):
            print("Resultados encontrados")
        else:
            print("Não foram encontrados resultados")

main()
