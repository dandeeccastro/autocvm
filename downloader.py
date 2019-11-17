import os 
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

apiURL = "https://www.rad.cvm.gov.br/ENET/frmDownloadDocumento.aspx?Tela=ext"
apiFile = open("fileLocationData.txt","r")
i = 0

def DownloadFile(numSequencia, numVersao, numProtocolo, descTipo, endFileName):
    url = apiURL + "&numSequencia=" + numSequencia + "&numVersao=" + numVersao + "&numProtocolo=" + numProtocolo + "&descTipo=" + descTipo + "&CodigoInstituicao=1"
    try:
        endFile = requests.get( url, allow_redirects=True, verify=False)
    except requests.ConnectionError:
        return 1
    except ConnectionResetError:
        return 1
    print(endFileName)
    file = open(endFileName,"wb")
    file.write(endFile.content)
    return 0
    
fileName = ""
os.chdir('./out')
for line in apiFile:
    if i%2 is 0:
        print("Am name")
        fileName = line.rsplit()
    else:
        print ("Am func")
        params = line.rstrip().split(',')
        alterador = DownloadFile(params[0],params[1],params[2],params[3],fileName[0])
        i -= alterador
    print(line)
    i += 1
