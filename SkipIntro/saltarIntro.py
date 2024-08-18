from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pynput import keyboard  # Necesitarás instalar pynput: pip install pynput

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


# Configura el servicio de ChromeDriver
service = Service('C:/ChromeDriver/chromedriver-win64/chromedriver.exe')
# Configura las opciones de Chrome
options = webdriver.ChromeOptions()
options.binary_location = r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'  # Ruta al binario de Brave
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# Desactiva las notificaciones de "Brave is being controlled by automated test software"
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Desactiva la barra de notificaciones de producto de Brave
prefs = {
    "profile.default_content_setting_values.notifications": 2  # Desactiva las notificaciones
}
options.add_experimental_option("prefs", prefs)
# Inicializa el navegador Chrome con las capacidades y opciones configuradas
driver = webdriver.Chrome(service=service, options=options)

# Maximiza la ventana del navegador
driver.maximize_window()

# Abre YouTube
url = "https://www3.animeflv.net/ver/death-note-1"
driver.get(url)


# Espera a que la página cargue completamente
time.sleep(10)


# Guarda el handle de la pestaña original
original_window = driver.current_window_handle
# Encuentra y hace clic en el elemento deseado usando CSS Selector
try:
    # Selecciona una opción por el data-id
    opcion = driver.find_element(By.CSS_SELECTOR, 'li[data-id="1"]')
    opcion.click()
    print("Elemento clickeado")
except Exception as e:
    print(f"Error al hacer clic en el elemento: {e}")

# Monitorea si se abre una nueva pestaña durante los próximos 5 segundos
new_window = None
timeout = time.time() + 5  # 5 segundos desde el momento del click
while time.time() < timeout:
    if len(driver.window_handles) > 1:
        # Si se abre una nueva pestaña, la guarda y sale del bucle
        new_window = [window for window in driver.window_handles if window != original_window][0]
        break
    time.sleep(0.5)  # Espera 0.5 segundos antes de verificar nuevamente

# Si se ha abierto una nueva pestaña, ciérrala
if new_window:
    driver.switch_to.window(new_window)
    driver.close()
    # Regresa a la pestaña original
    driver.switch_to.window(original_window)


#print("SLEEP")
#time.sleep(5)

# Cambia al contexto del iframe
iframe = driver.find_element(By.XPATH, '//iframe')
driver.switch_to.frame(iframe)

time.sleep(6)
# Obtén el tamaño de la ventana actual
window_size = driver.get_window_size()

# Calcula las coordenadas del centro de la pantalla
center_x = window_size['width'] // 2
center_y = window_size['height'] // 2

# Realiza un clic en el centro de la pantalla
actions = ActionChains(driver)

actions.move_by_offset(center_x - driver.execute_script("return window.screenX"), 
                       center_y - driver.execute_script("return window.screenY")).click().perform()
actions.click()



video_element = None

# Intenta encontrar el elemento <video> hasta que lo encuentre
while video_element is None:
    try:
        actions.click()
        # Intenta encontrar el elemento <video>
        video_element = driver.find_element(By.TAG_NAME, 'video')
        print("Elemento <video> encontrado.")
    except NoSuchElementException:
        # Si no se encuentra, espera un momento y sigue intentando
        print("Elemento <video> no encontrado, intentando de nuevo...")
        time.sleep(1)  # Espera 1 segundo antes de intentar de nuevo
time.sleep(2)

# Captura el tiempo actual
start_time = time.time()

i = 0
# Espera hasta que haya pasado 1 segundo desde que el video ha comenzado
while True:
    i += 1
    #print(f"vez numero {i}")
    current_time = driver.execute_script("return arguments[0].currentTime;", video_element)
    elapsed_time = time.time() - start_time
    
    if elapsed_time >= 1 and current_time > 0:
        break
    else:
        actions.click()
        print(f"CLICK NUMERO {i}")
    time.sleep(0.5)  # Revisa cada 0.1 segundos
time.sleep(1)
print("SALIO DEL WHILE")


driver.execute_script("arguments[0].requestFullscreen();", video_element)#NO SE POR QUE NO ESTA EJECUTANDO EL FULL SCREEN, DE IGUAL FORMA SIMPLEMENTE PODES VOS MISMOS PONER FULL SCREEN.
print("FULLSCREEN")
time.sleep(2)


# Variable para habilitar/deshabilitar la función de adelantar
can_skip = True

def on_press(key):
    global can_skip
    if key == keyboard.Key.tab and can_skip:
        # Ejecuta JavaScript para adelantar el video
        driver.execute_script("arguments[0].currentTime +=80;", video_element)  # Adelanta 80 segundos
        print("Video adelantado")
        can_skip = False  # Desactiva la funcionalidad hasta que cambie la URL

def on_change_url(new_url):
    global can_skip
    # Cambia la URL
    driver.get(new_url)
    # Espera a que la nueva página cargue completamente
    time.sleep(10)
    # Encuentra el nuevo elemento de video (esto depende del DOM del sitio, así que puede necesitar ajustes)
    global video_element
    video_element = driver.find_element(By.TAG_NAME, 'video')
    can_skip = True  # Vuelve a habilitar la funcionalidad

# Configura el listener de teclado
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Puedes llamar a `on_change_url` para cambiar la URL y habilitar nuevamente la funcionalidad
# Ejemplo:
# on_change_url('NUEVA_URL_DEL_CAPITULO')

try:
    # Mantén el script en ejecución para que el listener continúe funcionando
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Programa terminado")
finally:
    # Cierra el navegador
    driver.quit()


#FUNCION A IMPLENTAR, BOTON PARA PASAR AL SIGUIENTE CAPITULO, HACIENDO UN GET DEL LA URL SUMANDOLE 1 AL NUMERO DEL CAPITULO Y TAMBIEN QUIZAS UN BOTON PARA CAP ANTERIOR (AUNQUE ESTE ES MEDIO AL PEDO)