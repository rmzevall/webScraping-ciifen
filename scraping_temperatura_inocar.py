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

def archivo(texto, zona):
    bandera = False
    if (not os.path.exists("Scrapping-INOCAR-Temperatura-Superficial-Aire-" + zona + ".txt")):
        f = open("Scrapping-INOCAR-Temperatura-Superficial-Aire-" + zona + ".txt", "w")
        f.write(texto)
        f.close()
    else:
        textonuevo = texto.splitlines(True)
        scrapping = open("Scrapping-INOCAR-Temperatura-Superficial-Aire-" + zona + ".txt", "r")
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

        f = open("Scrapping-INOCAR-Temperatura-Superficial-Aire-" + zona + ".txt", "w")
        f.writelines(textoresultante)
        f.close()


def scraping(anioInicial,anioFinal,mesInicial,mesFinal):
    startTime = datetime.now()
    options = Options()
    #options.add_argument("--headless")
    #options.add_argument("--no-sandbox");
    #options.add_argument("--disable-dev-shm-usage");
    chrome = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    chrome.get("https://www.inocar.mil.ec/web/index.php/productos/estaciones-meteorologicas")

    try:
        WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
        "iframe[name=mapas_emc]")))
    finally:
        iframeimagen = chrome.find_element(By.NAME, "imagenes_emc")
        chrome.switch_to.frame(iframeimagen)
        tbodyanterior=chrome.page_source
        resetear_ventana = chrome.window_handles[0]
        chrome.switch_to.window(resetear_ventana)
        iframe = chrome.find_element(By.NAME,"mapas_emc")
        chrome.switch_to.frame(iframe)


        zonas = chrome.find_elements(By.CLASS_NAME, 'leaflet-marker-icon.leaflet-zoom-animated.leaflet-interactive')
        for indiceZona in range(len(zonas)):
            texto = "YYYY\tMM\tDD\tGrados(centigrados)\n"
            element = chrome.find_elements(By.CLASS_NAME, 'leaflet-marker-icon.leaflet-zoom-animated.leaflet-interactive')[indiceZona]
            chrome.execute_script("arguments[0].click();", element)
            WebDriverWait(chrome, 3).until(
                lambda drv: len(drv.find_elements(By.CLASS_NAME, "leaflet-popup.leaflet-zoom-animated")) == 1)
            element = chrome.find_element(By.CSS_SELECTOR, 'a[target=imagenes_emc]')
            chrome.execute_script("arguments[0].click();", element)
            zona = chrome.find_element(By.CLASS_NAME, "leaflet-popup-content").find_element(By.TAG_NAME,"b").get_attribute("innerHTML")

            chrome.switch_to.window(resetear_ventana)
            chrome.switch_to.frame(iframeimagen)
            if (indiceZona!=0):
                WebDriverWait(chrome, 3).until(lambda drv: drv.page_source != tbodyanterior)
                tbodyanterior=chrome.page_source
            element = chrome.find_element(By.CSS_SELECTOR, 'a')
            chrome.execute_script("arguments[0].click();", element)
            nueva_ventana = chrome.window_handles[1]
            chrome.switch_to.window(nueva_ventana)

            topframe = chrome.find_element(By.NAME, "topFrame")
            chrome.switch_to.frame(topframe)
            chrome.find_element(By.CSS_SELECTOR, "option[value=\"3\"]").click()
            chrome.switch_to.window(nueva_ventana)
            ##empezar loop en esta pagina recorriendo los años
            mainframe1 = chrome.find_element(By.NAME, "mainFrame1")
            chrome.switch_to.frame(mainframe1)
            leftframe = chrome.find_element(By.NAME, "leftFrame")
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
                    chrome.switch_to.window(nueva_ventana)
                    chrome.switch_to.frame(mainframe1)
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
                                init_text=""
                                try:
                                    chrome.switch_to.window(nueva_ventana)
                                    chrome.switch_to.frame(mainframe1)
                                    mainframe = chrome.find_element(By.NAME, "mainFrame")
                                    chrome.switch_to.frame(mainframe)
                                    WebDriverWait(chrome, 3).until(lambda drv: drv.find_element(By.ID,"container").get_attribute("innerHTML") != init_text)
                                except:
                                    time.sleep(30)
                                    chrome.switch_to.window(nueva_ventana)
                                    chrome.switch_to.frame(mainframe1)
                                    chrome.switch_to.frame(leftframe)

                                else:
                                    puntos=chrome.find_element(By.CLASS_NAME,"highcharts-markers.highcharts-series-0.highcharts-spline-series.highcharts-color-0.highcharts-tracker ")
                                    puntos=puntos.find_elements(By.TAG_NAME,"path")
                                    hover = ActionChains(chrome).move_to_element(puntos[1])
                                    hover.perform()
                                    puntosHover = chrome.find_element(By.CLASS_NAME,
                                                                 "highcharts-markers.highcharts-series-0.highcharts-spline-series.highcharts-color-0.highcharts-tracker.highcharts-series-hover")
                                    puntosHover = puntosHover.find_elements(By.TAG_NAME, "path")

                                    for punto in puntosHover:
                                        hover = ActionChains(chrome).move_to_element(punto)
                                        hover.perform()
                                        informacion = chrome.find_element(By.CLASS_NAME,
                                                                     "highcharts-label.highcharts-tooltip.highcharts-color-0")
                                        informacion = informacion.find_element(By.TAG_NAME,"text")
                                        datos = informacion.find_elements(By.TAG_NAME,"tspan")
                                        dia = datos[0].text
                                        grados = datos[3].text[0:-2].strip()
                                        if (float(dia) > 0 and float(dia) < 10):
                                            diaPrint = "0" + dia
                                        else:
                                            diaPrint = dia

                                        texto = texto + str(anio) + "\t" + mesyanio[0:2] + "\t" + diaPrint + "\t" + grados +"\n"


                                    esperar=False
                                    chrome.switch_to.window(nueva_ventana)
                                    chrome.switch_to.frame(mainframe1)
                                    chrome.switch_to.frame(leftframe)


                    chrome.switch_to.window(nueva_ventana)
                    chrome.switch_to.frame(topframe)
                    chrome.find_element(By.CSS_SELECTOR, "option[value=\"3\"]").click()
                    chrome.switch_to.window(nueva_ventana)
                    mainframe1 = chrome.find_element(By.NAME, "mainFrame1")
                    chrome.switch_to.frame(mainframe1)
                    leftframe = chrome.find_element(By.NAME, "leftFrame")
                    chrome.switch_to.frame(leftframe)

            archivo(texto, zona)
            chrome.switch_to.window(resetear_ventana)
            chrome.switch_to.frame(iframe)
    chrome.quit()
    print(datetime.now() - startTime)

#si se quiere ejecutar manualmente:
#scraping(anioInicial,anioFinal,mesInicial,mesFinal)
