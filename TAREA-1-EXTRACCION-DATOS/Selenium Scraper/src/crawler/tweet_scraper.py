"""
Implementación principal del scraper de tweets.

Este módulo contiene la lógica principal para extraer tweets relacionados
con la crisis energética en Ecuador, incluyendo geolocalización y análisis
de estrés durante los apagones.
"""

import time
import random
import re
from datetime import datetime
from typing import List, Set
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchElementException,
    TimeoutException
)
from src.models.tweet import Tweet
from src.utils.logger import logger
from src.utils.checkpoint_manager import CheckpointManager
from src.utils.csv_manager import CSVManager
from config.settings import (
    START_DATE,
    END_DATE,
    SCROLL_PAUSE_TIME,
    RETRY_COUNT,
    RADIO_BUSQUEDA
)

class TweetScraper:
    """Clase principal para el scraping de tweets."""

    def __init__(self, driver):
        """
        Inicializa el scraper con una instancia de WebDriver.

        Args:
            driver: Instancia de selenium.webdriver.Chrome
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.tweets_procesados = 0
        self.scroll_count = 0
        self.ultimo_tweet_id = None
        self.checkpoint_manager = None
        self.csv_manager = None

    def construir_query_url(self, termino_busqueda: str, coordenada: tuple) -> str:
        """
        Construye la URL de búsqueda para Twitter incluyendo geolocalización.

        Args:
            termino_busqueda: Término o hashtag a buscar
            coordenada: Tupla (lat, lon) del punto central de búsqueda

        Returns:
            str: URL de búsqueda formateada
        """
        lat, lon = coordenada
        termino_codificado = termino_busqueda.replace('#', '%23').replace(' ', '%20')
        geocode = f"geocode%3A{lat}%2C{lon}%2C{RADIO_BUSQUEDA}"

        url = (
            f"https://twitter.com/search?q={termino_codificado}%20"
            f"{geocode}%20"
            f"until%3A{END_DATE}%20since%3A{START_DATE}&src=typed_query&f=live"
        )
        logger.debug(f"URL de búsqueda construida: {url}")
        return url

    def extraer_tweets(self, termino_busqueda: str, coordenada: tuple, max_tweets: int = 100, continuar_anterior: bool = True) -> Set[Tweet]:
        """
        Extrae tweets basados en un término de búsqueda y coordenada.

        Args:
            termino_busqueda: Término o hashtag a buscar
            coordenada: Tupla (lat, lon) del punto central de búsqueda
            max_tweets: Número máximo de tweets a extraer
            continuar_anterior: Si debe continuar desde el último checkpoint

        Returns:
            Set[Tweet]: Conjunto de tweets únicos extraídos
        """
        # Inicializar managers con coordenada
        self.checkpoint_manager = CheckpointManager(termino_busqueda, coordenada)
        self.csv_manager = CSVManager(termino_busqueda, coordenada)

        # Cargar checkpoint si existe y se solicita continuar
        if continuar_anterior:
            checkpoint = self.checkpoint_manager.cargar_checkpoint()
            if checkpoint:
                self.tweets_procesados = checkpoint['tweets_procesados']
                self.scroll_count = checkpoint['scroll_count']
                self.ultimo_tweet_id = checkpoint['ultimo_tweet_id']
                logger.info(f"Continuando desde checkpoint - Tweets procesados: {self.tweets_procesados}")

        url_busqueda = self.construir_query_url(termino_busqueda, coordenada)
        logger.info(f"""Iniciando extracción:
            Término: {termino_busqueda}
            Coordenadas: {coordenada}
            Radio: {RADIO_BUSQUEDA}
            Periodo: {START_DATE} hasta {END_DATE}
        """)

        self.driver.get(url_busqueda)
        time.sleep(3)  # Espera adicional para carga completa

        # Verificar si hay resultados
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
            )
            logger.info("Tweets encontrados en la página")
        except TimeoutException:
            logger.warning(f"No se encontraron tweets para: {termino_busqueda} en coordenadas {coordenada}")
            return set()

        tweets_extraidos = set()
        ids_procesados = set()
        altura_previa = self.driver.execute_script('return document.body.scrollHeight')
        intentos_sin_nuevos = 0

        while len(tweets_extraidos) < max_tweets and intentos_sin_nuevos < 5:
            try:
                # Esperar a que los tweets sean visibles
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
                )

                # Obtener tweets visibles
                tweets_elementos = self.driver.find_elements(
                    By.CSS_SELECTOR, 'article[data-testid="tweet"]'
                )
                logger.debug(f"Encontrados {len(tweets_elementos)} tweets en la página actual")

                # Procesar tweets visibles
                for tweet_elemento in tweets_elementos:
                    if len(tweets_extraidos) >= max_tweets:
                        break

                    try:
                        # Verificar si el elemento está visible
                        if not self._is_element_in_viewport(tweet_elemento):
                            continue

                        # Scroll hasta el elemento
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", tweet_elemento)
                        time.sleep(0.5)

                        # Procesar tweet
                        tweet = self._procesar_tweet(tweet_elemento, termino_busqueda, coordenada)
                        if tweet and tweet.id not in ids_procesados:
                            tweets_extraidos.add(tweet)
                            ids_procesados.add(tweet.id)
                            self.tweets_procesados += 1
                            self.ultimo_tweet_id = tweet.id

                            # Mostrar progreso
                            if self.tweets_procesados % 10 == 0:
                                logger.info(f"Progreso: {self.tweets_procesados} tweets procesados")
                                # Guardar checkpoint y tweets
                                self.checkpoint_manager.guardar_checkpoint(
                                    self.ultimo_tweet_id,
                                    self.tweets_procesados,
                                    self.scroll_count
                                )
                                self.csv_manager.guardar_tweets(list(tweets_extraidos))

                    except Exception as e:
                        logger.error(f"Error al procesar tweet: {str(e)}")
                        continue

                # Scroll suave
                for _ in range(3):
                    self.driver.execute_script('window.scrollBy(0, 300);')
                    time.sleep(0.5)

                self.scroll_count += 1
                logger.debug(f"Scroll #{self.scroll_count} realizado")

                # Pausa aleatoria
                pausa = random.uniform(SCROLL_PAUSE_TIME * 0.8, SCROLL_PAUSE_TIME * 1.2)
                time.sleep(pausa)

                altura_actual = self.driver.execute_script('return document.body.scrollHeight')
                if altura_actual == altura_previa:
                    intentos_sin_nuevos += 1
                    logger.debug(f"Sin nuevos tweets: intento {intentos_sin_nuevos}/5")
                else:
                    intentos_sin_nuevos = 0
                altura_previa = altura_actual

                # Mostrar estadísticas periódicas
                if self.scroll_count % 5 == 0:
                    logger.info(f"""Estadísticas actuales:
                        Tweets encontrados: {len(tweets_extraidos)}
                        Scrolls realizados: {self.scroll_count}
                        Tweets únicos: {len(ids_procesados)}
                    """)

            except StaleElementReferenceException:
                logger.warning("Elemento obsoleto encontrado, continuando...")
                continue

        logger.info(f"""Extracción completada:
            Término: {termino_busqueda}
            Coordenadas: {coordenada}
            Total tweets: {len(tweets_extraidos)}
            Total scrolls: {self.scroll_count}
        """)

        # Guardar checkpoint final y tweets
        self.checkpoint_manager.guardar_checkpoint(
            self.ultimo_tweet_id,
            self.tweets_procesados,
            self.scroll_count
        )
        self.csv_manager.guardar_tweets(list(tweets_extraidos))
        self.checkpoint_manager.marcar_completado()

        return tweets_extraidos

    def _is_element_in_viewport(self, element) -> bool:
        """
        Verifica si un elemento está visible en la ventana actual.

        Args:
            element: Elemento WebElement a verificar

        Returns:
            bool: True si el elemento está visible
        """
        try:
            script = """
                var elem = arguments[0];
                var rect = elem.getBoundingClientRect();
                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
            """
            return self.driver.execute_script(script, element)
        except:
            return False

    def _procesar_tweet(self, elemento_tweet, termino_busqueda: str, coordenada: tuple) -> Tweet:
        """
        Procesa un elemento de tweet y extrae su información.

        Args:
            elemento_tweet: Elemento WebElement del tweet
            termino_busqueda: Término por el que se encontró el tweet
            coordenada: Tupla (lat, lon) de la ubicación de búsqueda

        Returns:
            Tweet: Objeto Tweet con la información extraída
        """
        try:
            # Extraer URL y ID
            link_elemento = elemento_tweet.find_element(
                By.XPATH, './/a[contains(@href, "/status/")]'
            )
            url_tweet = link_elemento.get_attribute('href')
            id_tweet = url_tweet.split('/')[-1]

            # Extraer información básica
            try:
                autor = elemento_tweet.find_element(
                    By.XPATH, './/span[contains(text(), "@")]'
                ).text.replace("@", "")
            except NoSuchElementException:
                return None

            try:
                nombre_completo = elemento_tweet.find_element(
                    By.XPATH, './/div[@data-testid="User-Name"]//span'
                ).text
            except NoSuchElementException:
                nombre_completo = ""

            try:
                contenido = elemento_tweet.find_element(
                    By.XPATH, './/div[@data-testid="tweetText"]'
                ).text
            except NoSuchElementException:
                contenido = ""

            timestamp_elem = elemento_tweet.find_element(By.XPATH, './/time')
            timestamp = timestamp_elem.get_attribute('datetime')

            # Extraer métricas
            retweets = self._extraer_metrica(elemento_tweet, 'retweet')
            likes = self._extraer_metrica(elemento_tweet, 'like')
            comentarios = self._extraer_metrica(elemento_tweet, 'reply')
            guardados = self._extraer_metrica(elemento_tweet, 'bookmark')

            # Extraer vistas
            try:
                vistas = elemento_tweet.find_element(
                    By.XPATH, "//*[@role='group']"
                ).text.split('\n')[-1]
            except NoSuchElementException:
                vistas = "0"

            # Extraer hashtags
            hashtags = tuple(re.findall(r'#\w+', contenido))

            # Crear objeto Tweet con coordenadas
            tweet = Tweet(
                id=id_tweet,
                autor=autor,
                nombre_completo=nombre_completo,
                contenido=contenido,
                fecha_publicacion=timestamp,
                retweets=retweets,
                likes=likes,
                hashtag=termino_busqueda,
                vistas=vistas,
                comentarios=comentarios,
                guardados=guardados,
                url_imagen=None,
                url_video=None,
                url_preview_video=None,
                hashtags=hashtags,
                url=url_tweet,
                coordenada_lat=coordenada[0],
                coordenada_lon=coordenada[1]
            )

            logger.debug(f"Tweet procesado: ID={tweet.id}, Autor=@{tweet.autor}")
            return tweet

        except Exception as e:
            logger.error(f"Error al procesar tweet {id_tweet if 'id_tweet' in locals() else 'desconocido'}: {str(e)}")
            return None

    def _extraer_metrica(self, elemento_tweet, tipo_metrica: str) -> str:
        """
        Extrae una métrica específica del tweet.

        Args:
            elemento_tweet: Elemento del tweet
            tipo_metrica: Tipo de métrica a extraer (retweet, like, etc.)

        Returns:
            str: Valor de la métrica
        """
        try:
            valor = elemento_tweet.find_element(
                By.XPATH, f'.//div[@data-testid="{tipo_metrica}"]'
            ).text
            return valor
        except NoSuchElementException:
            return "0"