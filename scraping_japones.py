from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox");
options.add_argument("--disable-dev-shm-usage");
browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
from bs4 import BeautifulSoup
import requests
import csv

browser.get("https://ds.data.jma.go.jp/tcc/tcc/products/climate/climatview/frame.php")

iframe = browser.find_element_by_tag_name("iframe")

browser.switch_to.default_content()

browser.switch_to.frame(iframe)

iframe_source = browser.page_source

soup= BeautifulSoup(iframe_source,'html.parser')

estaciones= soup.findAll('area')

izq=0
arriba=0
derecha=0
abajo=0
for i in estaciones:
    if(i.get('title').startswith('ISLA DE PASCUA')):
        izq=float(i.get('coords').split(",")[0])
    if (i.get('title').startswith('ACAJUTLA')):
        arriba = float(i.get('coords').split(",")[1])
    if (i.get('title').startswith('RECIFE')):
        derecha =float(i.get('coords').split(",")[0])
    if (i.get('title').startswith('USHUAIA AERO')):
        abajo =float(i.get('coords').split(",")[1])

for i in estaciones:
    coordenadas=i.get('coords').split(",")
    izqB=float(coordenadas[0]) >= izq
    arribaB=float(coordenadas[1]) >= arriba
    derechaB=float(coordenadas[0]) <= derecha
    abajoB=float(coordenadas[1]) <= abajo
    if(izqB  & arribaB & derechaB & abajoB):
        url2 = "https://ds.data.jma.go.jp/tcc/tcc/products/climate/climatview/" + i.get('href') + "&p=999"
        req = requests.get(url2)
        soup2 = BeautifulSoup(req.content, 'html.parser')
        datos = soup2.findAll('tr', class_='c')
        nombre= soup2.findAll('div', id='info')
        name=nombre[0].text.split("\n")[0]
        a=name.replace("/","-")
        b=a.replace("\\","-")
        with open(b+".csv", "w") as csvfile:
            fieldnames = ['Año/Mes', 'Mean Temp.[degC]', 'Max. Temp.(Monthly Mean)[degC]',
                            'Min. Temp.(Monthly Mean)[degC]', 'Precip.[mm]']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for i in datos:
                elementos = i.text.split("\n")[2:]
                writer.writerow({'Año/Mes': elementos[0],
                                    'Mean Temp.[degC]': elementos[1],
                                    'Max. Temp.(Monthly Mean)[degC]': elementos[2],
                                    'Min. Temp.(Monthly Mean)[degC]': elementos[3],
                                    'Precip.[mm]': elementos[4]})



