
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import base64
import time
import requests
from anticaptchaofficial.imagecaptcha import *


chrome_options=Options()
chrome_options.add_experimental_option("detach", True)
driver=webdriver.Chrome(options=chrome_options)
    
print("Navegador abierto")
driver.maximize_window()
driver.get("https://www.adres.gov.co/consulte-su-eps")
print("Página cargada")
driver.implicitly_wait(2)

iframe= driver.find_element(By.XPATH,'//*[@id="MSOPageViewerWebPart_WebPartWPQ3"]')
driver.switch_to.frame(iframe)

select= driver.find_element(By.XPATH,'//*[@id="tipoDoc"]')
tipo_doc_op=select.find_elements(By.TAG_NAME,'option')

seleccionar= Select( driver.find_element(By.XPATH,'//*[@id="tipoDoc"]'))
seleccionar.select_by_value("CC")


num_doc= driver.find_element(By.XPATH,'//*[@id="txtNumDoc"]')
num_doc.send_keys('1004235043')
captchaBool = False
while captchaBool is not True:
    try:
        # Capturar la imagen del captcha
      captchaImage = driver.find_element(By.XPATH, '//*[@id="Capcha_CaptchaImageUP"]')

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