import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from datetime import datetime
from selenium.webdriver.chrome.options import Options
import os


def archivo(texto):
    bandera = False
    if (not os.path.exists("Scrapping-INOCAR"+".txt")):
        f = open("Scrapping-INOCAR" + ".txt", "w")
        f.write(texto)
        f.close()
    else:
        textonuevo = texto.splitlines(True)
        scrapping = open("Scrapping-INOCAR" + ".txt", "r")
        lineas = scrapping.readlines()
        count=1
        count2=1
        textoresultante=[lineas[0]]
        if(len(lineas)>len(textonuevo)):
            listagrande=lineas[:]
            listapequenya=textonuevo[:]
        else:
            listapequenya=lineas[:]
            listagrande=textonuevo[:]

        while(count != len(listagrande)):
            anyopequenyo = int(listapequenya[count][0:4])
            mespequenyo = int(listapequenya[count][5:7])
            anyogrande = int(listagrande[count2][0:4])
            mesgrande = int(listagrande[count2][5:7])
            listapequenya[count]
            print(listapequenya[count])
            print(listagrande[count2])
            if(anyogrande<anyopequenyo):
                print(listapequenya[count])
                textoresultante.append(listapequenya[count])
                count=count+1
            if(anyogrande>anyopequenyo):
                textoresultante.append(listagrande[count2])
                count2 = count2 + 1
            if(anyogrande==anyopequenyo):
                if (mesgrande < mespequenyo):
                    textoresultante.append(listapequenya[count])
                    count = count + 1
                if(mesgrande>mespequenyo):
                    textoresultante.append(listagrande[count2])
                    count2 = count2 + 1
                if (mesgrande == mespequenyo):
                    textoresultante.append(listagrande[count2])
                    count2 = count2 + 1
                    count = count + 1

            if (count == len(listapequenya)):
                textoresultante = textoresultante+listagrande[count2:]
                break
            if (count2 == len(listagrande)):
                textoresultante = textoresultante+listapequenya[count:]
                break

        f = open("Scrapping-INOCAR" + ".txt", "w")
        f.writelines(textoresultante)
        f.close()


def scraping(anioInicial, anioFinal, mesInicial, mesFinal):
    startTime = datetime.now()
    texto="YYYY\tMM\tDD\tValor\n"
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox");
    options.add_argument("--disable-dev-shm-usage");
    chrome = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    chrome.get("https://www.inocar.mil.ec/web/index.php/precipitacion-en-guayaquil")
    chrome.maximize_window()
    try:
        element = WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
        "iframe")))
    finally:
        chrome.execute_script("window.open()")
        iframe = chrome.find_element(By.CSS_SELECTOR,"iframe")
        chrome.switch_to.frame(iframe)
        leftFrame = chrome.find_elements(By.ID,"leftFrame")[0]
        chrome.switch_to.frame(leftFrame)
        anios=len(chrome.find_elements(By.TAG_NAME, 'option'))
        for i in range(anios):
            anio=0
            if(i!=0):
                anio=int(chrome.find_elements(By.TAG_NAME, 'option')[i].text)
            WebDriverWait(chrome, 5).until(EC.presence_of_element_located(
                (By.TAG_NAME, 'option')))
            pasarAnio=False
            if (anio <= anioFinal and anio >= anioInicial):
                pasarAnio = True
            if (pasarAnio):
                chrome.find_elements(By.TAG_NAME, 'option')[i].click()
                resetear_ventana = chrome.window_handles[0]
                chrome.switch_to.window(resetear_ventana)
                chrome.switch_to.frame(iframe)
                chrome.switch_to.frame(leftFrame)
                meses= chrome.find_elements(By.CSS_SELECTOR, "tr[class*=\"row\"]  td  li  a")

                for j in range(len(meses)):
                    link = chrome.find_elements(By.CSS_SELECTOR, "tr[class*=\"row\"]  td  li  a")[j].get_attribute(
                        "href").__str__()
                    mesyanio = link.partition("?")[2]

                    mes = int(mesyanio[3:5])

                    pasarMes = False
                    if (mes <= mesFinal and mes >= mesInicial):
                        pasarMes = True

                    if (pasarMes):

                        esperar=True
                        while(esperar):
                            WebDriverWait(chrome, 5).until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, "tr[class*=\"row\"]  td  li  a")))

                            chrome.switch_to.window(chrome.window_handles[1])
                            #chrome.execute_script("arguments[0].click();", chrome.find_elements(By.CSS_SELECTOR, "tr[class*=\"row\"]  td  li  a")[j])
                            chrome.get(link)

                            init_text=""
                            try:
                                WebDriverWait(chrome, 3).until(lambda drv: drv.find_element(By.ID,"container").get_attribute("innerHTML") != init_text)
                            except:

                                time.sleep(30)
                                resetear_ventana = chrome.window_handles[0]
                                chrome.switch_to.window(resetear_ventana)
                                chrome.switch_to.frame(iframe)
                                chrome.switch_to.frame(leftFrame)
                            else:
                                soup = BeautifulSoup(chrome.page_source, "html.parser")
                                barrasContainer = soup.find("g", class_="highcharts-series highcharts-series-0 highcharts-column-series highcharts-color-undefined highcharts-tracker")
                                barras = barrasContainer.find_all("rect")
                                traslacionBarras=float(barrasContainer["transform"].partition(",")[0][10:])

                                diasEjeX=soup.find("g", class_="highcharts-axis-labels highcharts-xaxis-labels")
                                datos=soup.find_all("tspan", class_="highcharts-text-outline")
                                indiceDiasBarras = 1
                                for x in diasEjeX.find_all("text"):
                                    xdia=float(x["x"])
                                    diaPrint= ""
                                    if (float(x.text) > 0 and float(x.text) < 10):
                                        diaPrint= "0" + x.text
                                    else:
                                        diaPrint =x.text
                                    if (mes > 0 and mes < 10):
                                        mesPrint= "0" + str(mes)
                                    else:
                                        mesPrint =str(mes)
                                    if(not barras or len(barras)<indiceDiasBarras):

                                        texto = texto + str(anio) + "\t" + mesPrint + "\t" + diaPrint + "\t" + "-999\n"
                                    else:
                                        xinicial= float(barras[indiceDiasBarras - 1]["x"]) + traslacionBarras
                                        xfinal=xinicial+float(barras[indiceDiasBarras - 1]["width"])

                                        if(xinicial <= xdia and xdia <= xfinal):
                                            texto = texto + str(anio) + "\t" + mesPrint + "\t" + diaPrint + "\t" + datos[indiceDiasBarras - 1].text + "\n"
                                            indiceDiasBarras = indiceDiasBarras + 1
                                        else:
                                            texto= texto + str(anio) + "\t" + mesPrint + "\t" + diaPrint + "\t" + "-999\n"
                                esperar=False
                        resetear_ventana = chrome.window_handles[0]
                        chrome.switch_to.window(resetear_ventana)
                        chrome.switch_to.frame(iframe)
                        chrome.switch_to.frame(leftFrame)
                        time.sleep(1)
                    pasarMes = False

        archivo(texto)

        chrome.quit()
        print(datetime.now() - startTime)

#si se quiere ejecutar manualmente:
#scraping(anioInicial, anioFinal, mesInicial, mesFinal)

