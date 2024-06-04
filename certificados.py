import cv2
import easyocr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
import base64
import time


chrome_options=Options()
chrome_options.add_experimental_option("detach", True)
driver=webdriver.Chrome(chrome_options)
    
print("Navegador abierto")
driver.get("https://aplicaciones.adres.gov.co/bdua_internet/Pages/ConsultarAfiliadoWeb.aspx")
print("Página cargada")

select= driver.find_element(By.XPATH,'//*[@id="tipoDoc"]')
tipo_doc_op=select.find_elements(By.TAG_NAME,'option')

seleccionar= Select( driver.find_element(By.XPATH,'//*[@id="tipoDoc"]'))
seleccionar.select_by_value("CC")


num_doc= driver.find_element(By.XPATH,'//*[@id="txtNumDoc"]')
num_doc.send_keys('1004235043')

captchaBool = False
while captchaBool is not True:
    try:
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

        # Procesar la imagen con OpenCV
      img = cv2.imread('captcha.jpg')
      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      _, thresh = cv2.threshold(gray, 150, 200, cv2.THRESH_BINARY_INV)

        # Guardar la imagen procesada para el OCR
      cv2.imwrite('processed_captcha.jpg', thresh)

        # Usar EasyOCR para leer el texto de la imagen procesada
      reader = easyocr.Reader(['en'])
      result = reader.readtext('processed_captcha.jpg')

      print(result)
      for x in result:
        captchaResult= x[1]
        print(captchaResult)


      driver.find_element(By.XPATH, '//*[@id="Capcha_CaptchaTextBox"]').send_keys(captchaResult)
   
      driver.find_element(By.XPATH, '//*[@id="btnConsultar"]').click()
    except:
        print("Volviendo a intentar el captcha")