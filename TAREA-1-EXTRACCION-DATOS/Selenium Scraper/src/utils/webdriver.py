"""
Configuración y gestión del WebDriver de Selenium.

Este módulo maneja la configuración y inicialización del WebDriver,
incluyendo el proceso de login en Twitter/X.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config.settings import TWITTER_USERNAME, TWITTER_PASSWORD, WEBDRIVER_SETTINGS
from src.utils.logger import logger

class WebDriverManager:
    """Gestiona la configuración y el ciclo de vida del WebDriver."""

    def __init__(self):
        """Inicializa el WebDriver con las configuraciones especificadas."""
        self.driver = None

    def setup_driver(self):
        """Configura y retorna una instancia de Chrome WebDriver."""
        chrome_options = self._get_chrome_options()
        # Ruta manual al ChromeDriver
        service = Service("C:/Selenium/chromedriver.exe")

        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(WEBDRIVER_SETTINGS['implicit_wait'])
            self.driver.set_page_load_timeout(WEBDRIVER_SETTINGS['page_load_timeout'])
            return self.driver
        except Exception as e:
            logger.error(f"Error al inicializar WebDriver: {e}")
            raise

    def _get_chrome_options(self):
        """Configura las opciones de Chrome para el WebDriver."""
        chrome_options = Options()

        # Configurar modo headless según la configuración
        if WEBDRIVER_SETTINGS['headless']:
            chrome_options.add_argument('--headless=new')  # Nueva sintaxis para Chrome moderno
            chrome_options.add_argument('--disable-gpu')
        else:
            # Configuraciones para modo visible
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--window-size=1920,1080')

        # Configuraciones comunes
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--disable-popup-blocking')

        # Configuraciones adicionales para mejor rendimiento
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Configuraciones para evitar detección
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        return chrome_options

    def login_twitter(self):
        """Realiza el proceso de login en Twitter/X."""
        try:
            logger.info("Iniciando proceso de login en Twitter...")
            self.driver.get('https://twitter.com/i/flow/login')
            time.sleep(5)  # Esperar a que cargue completamente la página

            # Esperar y llenar usuario
            wait = WebDriverWait(self.driver, 15)
            username_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
            )
            username_input.send_keys(TWITTER_USERNAME)
            username_input.send_keys(Keys.RETURN)
            logger.info("Usuario ingresado...")
            time.sleep(3)

            try:
                # Verificar si aparece el campo de "unusual activity"
                unusual_activity = self.driver.find_element(By.CSS_SELECTOR, 'input[data-testid="ocfEnterTextTextInput"]')
                if unusual_activity:
                    logger.warning("Detectada solicitud de verificación adicional...")
                    if not WEBDRIVER_SETTINGS['headless']:
                        # Si estamos en modo visible, dar tiempo al usuario para verificar manualmente
                        logger.info("Por favor, complete la verificación manualmente. Tienes 30 segundos...")
                        time.sleep(30)  # Esperar 30 segundos para verificación manual
                        return True
                    else:
                        logger.error("No se puede completar la verificación en modo headless")
                        return False
            except NoSuchElementException:
                pass

            # Esperar y llenar contraseña
            try:
                password_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
                )
                password_input.send_keys(TWITTER_PASSWORD)
                password_input.send_keys(Keys.RETURN)
                logger.info("Contraseña ingresada...")
            except TimeoutException:
                logger.error("No se pudo encontrar el campo de contraseña")
                return False

            # Esperar a que se complete el login verificando un elemento de la página principal
            try:
                wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="primaryColumn"]'))
                )
                logger.info("Login completado exitosamente")
                return True
            except TimeoutException:
                logger.error("No se pudo verificar el login exitoso")
                return False

        except TimeoutException as e:
            logger.error(f"Timeout durante el proceso de login: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error durante el proceso de login: {str(e)}")
            return False

    def quit(self):
        """Cierra el WebDriver y libera recursos."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver cerrado correctamente")
            except Exception as e:
                logger.error(f"Error al cerrar WebDriver: {e}")

def setup_web_driver():
    """
    Función de utilidad para configurar y retornar una instancia de WebDriver.

    Returns:
        webdriver.Chrome: Instancia configurada del WebDriver
    """
    driver_manager = WebDriverManager()
    driver = driver_manager.setup_driver()
    if driver_manager.login_twitter():
        return driver
    else:
        driver_manager.quit()
        raise Exception("No se pudo completar el proceso de login en Twitter")