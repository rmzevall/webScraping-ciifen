import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import os


def archivo(listatexto, zona):
    bandera = False
    if (not os.path.exists("Scrapping-INOCAR-acumulado-mensual-"+zona+".txt")):
        f = open("Scrapping-INOCAR-acumulado-mensual-"+zona+".txt", "w")
        f.writelines(listatexto)
        f.close()
    else:
        textonuevo = listatexto
        scrapping = open("Scrapping-INOCAR-acumulado-mensual-"+zona+".txt", "r")
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
            if(anyogrande<anyopequenyo):
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

        f = open("Scrapping-INOCAR-acumulado-mensual-"+zona+".txt", "w")
        f.writelines(textoresultante)
        f.close()


def scraping(anioInicial,anioFinal,mesInicial,mesFinal):
    startTime = datetime.now()
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1920,1080")
    options.add_argument("--no-sandbox");
    options.add_argument("--disable-dev-shm-usage");
    chrome = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    chrome.get("https://www.inocar.mil.ec/web/index.php/precipitacion-por-estacion")

    try:
        WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
        'div[itemprop=articleBody] iframe')))
    finally:
        dicc_zonas = {}
        cabecera = "YYYY\tMM\tInformacion-Mes(mm)\tInformacion-Normal-Mes(mm)\n"
        resetear_ventana = chrome.window_handles[0]
        iframe = chrome.find_element(By.CSS_SELECTOR, 'div[itemprop=articleBody]').find_element(By.TAG_NAME,"iframe")
        chrome.switch_to.frame(iframe)
        leftframe = chrome.find_element(By.ID, "leftFrame")
        chrome.switch_to.frame(leftframe)
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
                chrome.switch_to.window(resetear_ventana)
                chrome.switch_to.frame(iframe)
                chrome.switch_to.frame(leftframe)
                WebDriverWait(chrome, 5).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "tr[class*=\"row\"]  td  li  a")))
                meses= chrome.find_elements(By.CSS_SELECTOR, "tr[class*=\"row\"]  td  li  a")
                for j in range(len(meses)):
                    link = chrome.find_elements(By.CSS_SELECTOR, "tr[class*=\"row\"]  td  li  a")[j].get_attribute("href")
                    mesyanio = str(link)[-12:]
                    mes = int(mesyanio[0:2])
                    pasarMes = False
                    if (mes <= mesFinal and mes >= mesInicial):
                        pasarMes = True
                    if (pasarMes):
                        chrome.find_elements(By.CSS_SELECTOR, "tr[class*=\"row\"]  td  li  a")[j].click()
                        esperar=True
                        while(esperar):
                            try:
                                chrome.switch_to.window(resetear_ventana)
                                chrome.switch_to.frame(iframe)
                                mainframe = chrome.find_element(By.ID, "mainFrame")
                                chrome.switch_to.frame(mainframe)
                                init_text = ""

                                WebDriverWait(chrome, 3).until(lambda drv: drv.find_element(By.ID,"container").get_attribute("innerHTML") != init_text)

                            except:
                                time.sleep(30)
                                chrome.switch_to.window(resetear_ventana)
                                chrome.switch_to.frame(iframe)
                                chrome.switch_to.frame(leftframe)

                            else:


                                scroll = chrome.find_element(By.CLASS_NAME,
                                                             "highcharts-series.highcharts-series-1.highcharts-column-series.highcharts-color-1.highcharts-tracker")
                                chrome.execute_script("arguments[0].scrollIntoView(true);", scroll)
                                barras = scroll.find_elements(By.TAG_NAME, "rect")
                                hover = ActionChains(chrome).move_to_element(barras[0])
                                hover.perform()
                                back = chrome.find_element(By.CLASS_NAME, "highcharts-plot-background")
                                ancho = int(back.get_attribute("width"))
                                division = ancho / (len(barras))
                                puntoHover= division/2
                                for i in range(len(barras)):
                                    ActionChains(chrome).move_to_element_with_offset(back, puntoHover , 5).click().perform()
                                    puntoHover=puntoHover+division
                                    chrome.execute_script("arguments[0].scrollIntoView(true);", scroll)
                                    #esto funciona, meterle un for qaue divida pixeles del background entre len de la lista de barras
                                    #meterlo en un for e ir recorriendo segun esa division
                                    informacion = chrome.find_element(By.CSS_SELECTOR,
                                                                 "div.highcharts-label.highcharts-tooltip")
                                    nombre = informacion.find_element(By.TAG_NAME,"b").text
                                    datos = informacion.find_elements(By.TAG_NAME, "td")
                                    precipitacionMes=datos[1].text.split(" ")[0]
                                    precipitacionNormalMes = datos[3].text.split(" ")[0]

                                    texto =str(anio) + "\t" + mesyanio[0:2] + "\t"+ precipitacionMes + "\t" +precipitacionNormalMes +"\n"
                                    if nombre in dicc_zonas:
                                        dicc_zonas[nombre].append(texto)
                                    else:
                                        dicc_zonas[nombre] = [cabecera,texto]

                                esperar=False
                                chrome.switch_to.window(resetear_ventana)
                                chrome.switch_to.frame(iframe)
                                chrome.switch_to.frame(leftframe)

                chrome.switch_to.window(resetear_ventana)
                chrome.switch_to.frame(iframe)
                chrome.switch_to.frame(leftframe)
        for zona,listatexto in dicc_zonas.items():
            archivo(listatexto,zona)

        chrome.quit()
        print(datetime.now() - startTime)

#si se quiere ejecutar manualmente:
#scraping(anioInicial,anioFinal,mesInicial,mesFinal)
