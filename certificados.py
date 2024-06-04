
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import time
import requests
from anticaptchaofficial.imagecaptcha import *

#Configuracion del navegador 
chrome_options=Options()
chrome_options.add_experimental_option("detach", True)
driver=webdriver.Chrome(options=chrome_options)
print("Navegador abierto")

driver.maximize_window()

driver.get("https://www.adres.gov.co/consulte-su-eps")
print("Página cargada")
driver.implicitly_wait(2)

#Se cambia el contexto al iframe que contiene el formulario
iframe= driver.find_element(By.XPATH,'//*[@id="MSOPageViewerWebPart_WebPartWPQ3"]')
driver.switch_to.frame(iframe)

#Seleccion del tipo de documento de la lista desplegable
select= driver.find_element(By.XPATH,'//*[@id="tipoDoc"]')
tipo_doc_op=select.find_elements(By.TAG_NAME,'option')
seleccionar= Select( driver.find_element(By.XPATH,'//*[@id="tipoDoc"]'))
seleccionar.select_by_value("CC")

#Ingreso del numero de docuento
num_doc= driver.find_element(By.XPATH,'//*[@id="txtNumDoc"]')
num_doc.send_keys('1004235043')

#Resolver el captcha
captchaBool = False
while captchaBool is not True:
    try:
        # Capturar la imagen del captcha
      captchaImage = driver.find_element(By.XPATH, '//*[@id="Capcha_CaptchaImageUP"]')
      #Script de javascript 
      captchaImageSave = driver.execute_async_script("""
          var ele = arguments[0], callback = arguments[1];
          ele.addEventListener('load', function fn(){
              ele.removeEventListener('load', fn, false);
              var cnv = document.createElement('canvas');
              cnv.width = this.width; cnv.height = this.height;
              cnv.getContext('2d').drawImage(this, 0, 0);
              callback(cnv.toDataURL('image/jpeg').substring(22));
          }, false);
           ele.dispatchEvent(new Event('load'));
        """, captchaImage)

      with open(r"captcha.jpg", 'wb') as f:
          f.write(base64.b64decode(captchaImageSave))

        # Resolver el captcha usando anticaptcha API
      solver = imagecaptcha()
      solver.set_verbose(1)
      solver.set_key("a59d40aabee57e96838a4f338b2aca1d")
      solver.set_soft_id(0)

      captcha_text = solver.solve_and_return_solution("captcha.jpg")
      print(captcha_text)
      if captcha_text != 0:
          print("Captcha text: " + captcha_text)
          driver.find_element(By.XPATH, '//*[@id="Capcha_CaptchaTextBox"]').send_keys(captcha_text)
          driver.find_element(By.XPATH, '//*[@id="btnConsultar"]').click()
          captchaBool = True
      else:
          print("Task finished with error: " + solver.error_code)
          captchaBool = False
          time.sleep(2)  # Esperar un momento antes de intentar nuevamente
    except Exception as e:
      print(f"Volviendo a intentar el captcha debido a: {e}")
      time.sleep(2) 


# Esperar la apertura de una nueva pestaña
WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

# Cambiar al nuevo handle de la pestaña
for handle in driver.window_handles:
    if handle != driver.current_window_handle:
        driver.switch_to.window(handle)
        break
    
time.sleep(5)

# Extraer el HTML de la página
page_html = driver.page_source

# Guardar el HTML en un archivo
with open("resultado.html", "w", encoding='utf-8') as file:
    file.write(page_html)

print("HTML de la página guardado en resultado.html")
