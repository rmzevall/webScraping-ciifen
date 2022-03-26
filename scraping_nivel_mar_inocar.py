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
    if (not os.path.exists("Scrapping-INOCAR-Nivel-Del-Mar-" + zona + ".txt")):
        f = open("Scrapping-INOCAR-Nivel-Del-Mar-" + zona + ".txt", "w")
        f.write(texto)
        f.close()
    else:
        textonuevo = texto.splitlines(True)
        scrapping = open("Scrapping-INOCAR-Nivel-Del-Mar-" + zona + ".txt", "r")
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
            "YYYY\tMM\tDD\tHH:MM\tNivel_Mar(m)\n"

            anyopequenyo = listapequenya[count][0:4]
            mespequenyo = listapequenya[count][5:7]
            diapequenyo = listapequenya[count][8:10]
            horapequenya = listapequenya[count][11:16]
            anyogrande = listagrande[count2][0:4]
            mesgrande = listagrande[count2][5:7]
            diagrande = listagrande[count2][8:10]
            horagrande = listagrande[count2][11:16]
            stringfechapequenya=diapequenyo+"/"+mespequenyo+"/"+anyopequenyo+" "+horapequenya
            fechapequenya=datetime.strptime(stringfechapequenya, '%d/%m/%Y %H:%M')
            stringfechagrande = diagrande + "/" + mesgrande + "/" + anyogrande + " " + horagrande
            fechagrande=datetime.strptime(stringfechagrande, '%d/%m/%Y %H:%M')
            if(fechagrande<fechapequenya):
                textoresultante.append(listapequenya[count])
                count=count+1
            if(fechagrande>fechapequenya):
                textoresultante.append(listagrande[count2])
                count2 = count2 + 1
            if(fechagrande==fechapequenya):
                textoresultante.append(listagrande[count2])
                count2 = count2 + 1
                count = count + 1

            if (count == len(listapequenya)):
                textoresultante = textoresultante+listagrande[count2:]
                break
            if (count2 == len(listagrande)):
                textoresultante = textoresultante+listapequenya[count:]
                break

        f = open("Scrapping-INOCAR-Nivel-Del-Mar-" + zona + ".txt", "w")
        f.writelines(textoresultante)
        f.close()


def scraping():
    startTime = datetime.now()
    options = Options()
    options.add_argument("--headless")
    options.add_argument("window-size=1920,1080")
    options.add_argument("--no-sandbox");
    options.add_argument("--disable-dev-shm-usage");
    chrome = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    chrome.get("https://www.inocar.mil.ec/web/index.php/productos/estaciones-de-monitoreo")

    try:
        WebDriverWait(chrome, 10).until(EC.presence_of_element_located((By.TAG_NAME,
        "iframe")))
    except:
        print("no se puede acceder a la pagina web")
    else:
        fechapequenya = datetime.strptime("12:00", '%H:%M')
        print(fechapequenya)
        resetear_ventana = chrome.window_handles[0]
        chrome.switch_to.window(resetear_ventana)
        iframe = chrome.find_element(By.TAG_NAME,"iframe")
        chrome.switch_to.frame(iframe)
        tbodyanterior = chrome.page_source
        #scroll = chrome.find_element(By.ID, 'map')
        #chrome.execute_script("arguments[0].scrollIntoView(true);", scroll)
        zonas = chrome.find_elements(By.CLASS_NAME, 'leaflet-marker-icon.leaflet-zoom-animated.leaflet-interactive')
        modalbodyanterior=chrome.page_source
        for indiceZona in range(len(zonas)):
            texto = "YYYY\tMM\tDD\tHH:MM\tNivel_Mar(m)\n"

            element = chrome.find_elements(By.CLASS_NAME, 'leaflet-marker-icon.leaflet-zoom-animated.leaflet-interactive')[indiceZona]
            chrome.execute_script("arguments[0].click();", element)
            zona = chrome.find_element(By.ID, "feature-title").get_attribute("innerHTML").removeprefix("Estación de monitoreo ")
            print(zona)
            iframemodal = chrome.find_element(By.TAG_NAME,"iframe")
            chrome.switch_to.frame(iframemodal)


            WebDriverWait(chrome, 3).until(lambda drv: drv.page_source != tbodyanterior)

            back = chrome.find_element(By.CLASS_NAME, "highcharts-plot-background")
            ancho = int(back.get_attribute("width"))
            strAnterior=""
            for i in range(ancho+1):
                ActionChains(chrome).move_to_element_with_offset(back, i, 5).click().perform()
                try:
                    claseInformacion=chrome.find_element(By.CLASS_NAME,"highcharts-label.highcharts-tooltip.highcharts-color-0")
                except:
                    pass
                else:
                    textInformacion = claseInformacion.find_elements(By.TAG_NAME, "tspan")
                    stringTiempo = textInformacion[0].text
                    nivelMetros = textInformacion[2].text.split(" ")[0]
                    listaString = stringTiempo.split()

                    dia = listaString[1]

                    mes = str(datetime.strptime(listaString[2],"%B").month)

                    anio = listaString[3]

                    hora = listaString[-1]

                    if (int(dia) > 0 and int(dia) < 10):
                        dia = "0" + str(int(dia))
                    if (int(mes) > 0 and int(mes) < 10):
                        mes = "0" + str(int(mes))
                    strInfo = str(anio) + "\t" + mes + "\t" + dia + "\t" + hora + "\t" + nivelMetros + "\n"
                    if strInfo != strAnterior:
                        texto = texto + strInfo
                        strAnterior = strInfo


            archivo(texto, zona)
            chrome.switch_to.window(resetear_ventana)
            chrome.switch_to.frame(iframe)
    chrome.quit()
    print(datetime.now() - startTime)

#si se quiere ejecutar manualmente:
#scraping()