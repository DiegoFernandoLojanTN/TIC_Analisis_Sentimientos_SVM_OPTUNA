"""
Módulo principal de scraping para el Twitter Scraper.
Contiene la lógica para extraer tweets de Twitter/X.
"""
import asyncio
import json
import os
import random
import time
from datetime import datetime
import backoff
from twikit import Client, TooManyRequests
from colorama import Fore, Style, Back, init

from config.settings import (
    TWITTER_USERNAME, TWITTER_PASSWORD, TWITTER_EMAIL,
    COOKIES_FILE, CHECKPOINT_FILE, DATE_START, DATE_END,
    NONRELEVANT_DIR, MAX_RETRIES, RETRY_DELAY
)
from config.keywords import PALABRAS_CLAVE, COMBINACIONES_BUSQUEDA
from modules.filters import filtrar_tweet, ubicacion_ecuador
from modules.utils import (
    log_info, log_success, log_warning, log_error,
    save_checkpoint, load_checkpoint, backoff_hdlr,
    simulate_human_behavior
)

# Inicializar colorama
init(autoreset=True)

class TwitterScraper:
    """Clase principal para extraer tweets de Twitter/X."""

    def __init__(self, logger, progress_tracker=None):
        """
        Inicializa el scraper.

        Args:
            logger: Objeto logger para registrar eventos
            progress_tracker: Objeto para seguimiento de progreso
        """
        self.logger = logger
        self.progress_tracker = progress_tracker
        self.client = None
        self.tweets_count = 0
        self.tweets_personales = 0
        self.tweets_filtrados = 0
        self.estadisticas = {categoria: 0 for categoria in PALABRAS_CLAVE.keys()}
        self.checkpoint_data = None
        self.tweet_ids_procesados = set()  # Para evitar duplicados
        self.nonrelevant_tweets = []  # Para almacenar tweets no relevantes
        self.consecutive_errors = 0
        self.last_query_time = None
        self.blocked_status = False

    async def inicializar(self):
        """
        Inicializa el cliente de Twitter y carga el checkpoint si existe.

        Returns:
            bool: True si la inicialización fue exitosa, False en caso contrario
        """
        try:
            # Inicializar cliente
            log_info(self.logger, "Autenticando en Twitter/X...")
            self.client = Client(language='es')

            # Verificar si existe el archivo de cookies
            if os.path.exists(COOKIES_FILE):
                log_info(self.logger, f"Cargando cookies existentes desde: {COOKIES_FILE}")
                try:
                    self.client.load_cookies(COOKIES_FILE)
                    log_success(self.logger, "Cookies cargadas correctamente")
                except Exception as e:
                    log_warning(self.logger, f"Error al cargar cookies: {e}. Intentando iniciar sesión directamente...")
                    await self._login_with_retry()
            else:
                log_warning(self.logger, f"No se encontró el archivo de cookies en {COOKIES_FILE}. Iniciando sesión por primera vez...")
                await self._login_with_retry()

            # Verificar si la autenticación fue exitosa
            try:
                # Intentar una operación simple para verificar la autenticación
                log_info(self.logger, "Verificando autenticación...")
                await self.client.get_home_timeline(count=1)
                log_success(self.logger, "Autenticación exitosa")
            except Exception as e:
                log_error(self.logger, f"Error al verificar autenticación: {e}")
                log_warning(self.logger, "Intentando iniciar sesión directamente como respaldo...")
                await self._login_with_retry()

            # Cargar checkpoint si existe
            self.checkpoint_data = load_checkpoint(CHECKPOINT_FILE)
            if self.checkpoint_data:
                log_info(self.logger, f"Checkpoint encontrado. Reanudando desde {self.checkpoint_data['tweets_count']} tweets")
                self.tweets_count = self.checkpoint_data['tweets_count']
                self.tweets_personales = self.checkpoint_data.get('tweets_personales', 0)
                self.tweets_filtrados = self.checkpoint_data.get('tweets_filtrados', 0)
                self.estadisticas = self.checkpoint_data.get('estadisticas', self.estadisticas)
                self.tweet_ids_procesados = set(self.checkpoint_data.get('tweet_ids', []))

            return True
        except Exception as e:
            log_error(self.logger, f"Error al inicializar el scraper: {e}")
            return False

    async def _login_with_retry(self, max_retries=3):
        """
        Intenta iniciar sesión con reintentos.

        Args:
            max_retries (int): Número máximo de intentos

        Returns:
            bool: True si el inicio de sesión fue exitoso

        Raises:
            Exception: Si no se pudo iniciar sesión después de los reintentos
        """
        for attempt in range(max_retries):
            try:
                log_info(self.logger, f"Intento de inicio de sesión {attempt+1}/{max_retries}...")
                await self.client.login(
                    auth_info_1=TWITTER_USERNAME,
                    auth_info_2=TWITTER_EMAIL,
                    password=TWITTER_PASSWORD
                )

                # Guardar cookies para futuros usos
                log_info(self.logger, "Guardando cookies para futuros usos...")
                os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)
                self.client.save_cookies(COOKIES_FILE)
                log_success(self.logger, "Cookies guardadas correctamente")
                return True
            except Exception as e:
                log_warning(self.logger, f"Error en intento {attempt+1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)  # Espera incremental
                    log_info(self.logger, f"Esperando {wait_time} segundos antes del siguiente intento...")
                    await asyncio.sleep(wait_time)
                else:
                    log_error(self.logger, "Se agotaron los intentos de inicio de sesión")
                    raise

    def generar_consulta(self):
        """
        Genera una consulta aleatoria basada en las palabras clave.

        Returns:
            tuple: (consulta, categoria) donde consulta es la cadena de búsqueda y categoria es la categoría seleccionada
        """
        # Decidir si usar una combinación predefinida o generar una aleatoria
        if random.random() < 0.7:  # 70% de probabilidad de usar combinación predefinida
            manifestacion, contexto = random.choice(COMBINACIONES_BUSQUEDA)

            # Determinar la categoría de la manifestación
            categoria_seleccionada = None
            for categoria, palabras in PALABRAS_CLAVE.items():
                if categoria not in ["crisis_energetica", "contexto_ecuador"] and manifestacion in palabras:
                    categoria_seleccionada = categoria
                    break

            # Si no se encontró la categoría, asignar una por defecto
            if not categoria_seleccionada:
                categoria_seleccionada = "expresiones_malestar"

            # Construir la consulta
            query = f'"{manifestacion}" {contexto} -filter:retweets -filter:replies lang:es since:{DATE_START} until:{DATE_END}'
        else:
            # Seleccionar una palabra clave de crisis energética
            crisis = random.choice(PALABRAS_CLAVE["crisis_energetica"])

            # Seleccionar una palabra clave de contexto Ecuador
            contexto = random.choice(PALABRAS_CLAVE["contexto_ecuador"])

            # Seleccionar una categoría aleatoria de manifestaciones
            categorias = ["estres_directo", "manifestaciones_fisicas", "manifestaciones_psicologicas", "expresiones_malestar", "impacto_actividades"]
            categoria_seleccionada = random.choice(categorias)

            # Seleccionar una palabra clave de la categoría seleccionada
            manifestacion = random.choice(PALABRAS_CLAVE[categoria_seleccionada])

            # Construir la consulta
            query = f'({manifestacion}) ({crisis}) ({contexto}) -filter:retweets -filter:replies lang:es since:{DATE_START} until:{DATE_END}'

        return query, categoria_seleccionada

    async def obtener_tweets(self, tweets, query):
        """
        Obtiene tweets basados en la consulta proporcionada, con reintentos automáticos.

        Args:
            tweets: Objeto de paginación de tweets o None para iniciar una nueva búsqueda
            query (str): Consulta de búsqueda

        Returns:
            object: Objeto de paginación de tweets
        """
        # Simular comportamiento humano
        await simulate_human_behavior()

        # Verificar si estamos bloqueados
        if self.blocked_status:
            wait_time = random.randint(300, 900)  # 5-15 minutos
            log_warning(self.logger, f"Posible bloqueo detectado. Esperando {wait_time} segundos antes de reintentar...")
            await asyncio.sleep(wait_time)
            self.blocked_status = False

        # Registrar tiempo de consulta para controlar la frecuencia
        current_time = time.time()
        if self.last_query_time:
            elapsed = current_time - self.last_query_time
            if elapsed < 5:  # Asegurar al menos 5 segundos entre consultas
                await asyncio.sleep(5 - elapsed)

        self.last_query_time = time.time()

        try:
            if tweets is None:
                log_info(self.logger, f"Obteniendo tweets con la consulta: {query}")
                tweets = await self.client.search_tweet(query, product='Top')
            else:
                wait_time = random.randint(8, 15)  # Más tiempo entre páginas
                log_info(self.logger, f"Obteniendo siguientes tweets después de {wait_time} segundos...")
                await asyncio.sleep(wait_time)
                tweets = await tweets.next()

            # Resetear contador de errores consecutivos
            self.consecutive_errors = 0
            return tweets

        except TooManyRequests:
            self.consecutive_errors += 1
            self.blocked_status = True
            wait_time = min(60 * (2 ** self.consecutive_errors), 3600)  # Espera exponencial, máximo 1 hora
            log_warning(self.logger, f"Límite de solicitudes alcanzado. Esperando {wait_time} segundos...")
            await asyncio.sleep(wait_time)
            return None

        except Exception as e:
            self.consecutive_errors += 1
            wait_time = min(30 * self.consecutive_errors, 600)  # Espera incremental, máximo 10 minutos
            log_error(self.logger, f"Error al obtener tweets: {e}. Esperando {wait_time} segundos...")
            await asyncio.sleep(wait_time)
            return None

    def procesar_tweet(self, tweet, categoria, consulta, exporters, nonrelevant_exporter=None):
        """
        Procesa un tweet, lo filtra y lo exporta si es relevante.

        Args:
            tweet: Objeto tweet de la API
            categoria (str): Categoría de la consulta
            consulta (str): Consulta utilizada
            exporters (list): Lista de exportadores para guardar el tweet
            nonrelevant_exporter: Exportador para tweets no relevantes

        Returns:
            bool: True si el tweet fue procesado y exportado, False en caso contrario
        """
        # Verificar si ya procesamos este tweet
        if tweet.id in self.tweet_ids_procesados:
            return False

        # Marcar como procesado
        self.tweet_ids_procesados.add(tweet.id)

        # Aplicar filtros
        incluir, motivo = filtrar_tweet(tweet)

        # Verificar ubicación
        es_ecuador = ubicacion_ecuador(tweet)

        # Crear enlace al tweet
        tweet_link = f'https://x.com/{tweet.user.name}/status/{tweet.id}'

        if not incluir or not es_ecuador:
            self.tweets_filtrados += 1

            # Guardar tweet no relevante si hay un exportador
            if nonrelevant_exporter:
                nonrelevant_data = {
                    'id': tweet.id,
                    'usuario': tweet.user.name,
                    'texto': tweet.text,
                    'fecha': tweet.created_at,
                    'retweets': tweet.retweet_count,
                    'likes': tweet.favorite_count,
                    'enlace': tweet_link,
                    'motivo_filtrado': motivo if not incluir else "no_ecuador" if not es_ecuador else "desconocido",
                    'consulta': consulta
                }
                nonrelevant_exporter.export(nonrelevant_data)

            return False

        # Incrementar contadores
        self.tweets_count += 1
        self.estadisticas[categoria] += 1
        if motivo == "expresion_personal":
            self.tweets_personales += 1

        # Preparar datos del tweet
        tweet_data = {
            'id': tweet.id,
            'usuario': tweet.user.name,
            'texto': tweet.text,
            'fecha': tweet.created_at,
            'retweets': tweet.retweet_count,
            'likes': tweet.favorite_count,
            'enlace': tweet_link,
            'categoría': categoria,
            'consulta': consulta,
            'es_personal': motivo == "expresion_personal",
            'ubicación': getattr(tweet.user, 'location', 'No disponible')
        }

        # Exportar a todos los formatos
        for exporter in exporters:
            exporter.export(tweet_data)

        # Actualizar barra de progreso si existe
        if self.progress_tracker:
            self.progress_tracker.update()

        # Guardar checkpoint cada 10 tweets
        if self.tweets_count % 10 == 0:
            self.guardar_checkpoint()
            log_success(self.logger, f"Obtenidos {self.tweets_count} tweets ({self.tweets_personales} expresiones personales)")

        return True

    def guardar_checkpoint(self):
        """Guarda el estado actual como punto de control."""
        checkpoint = {
            'tweets_count': self.tweets_count,
            'tweets_personales': self.tweets_personales,
            'tweets_filtrados': self.tweets_filtrados,
            'estadisticas': self.estadisticas,
            'tweet_ids': list(self.tweet_ids_procesados),
            'timestamp': datetime.now().isoformat()
        }
        save_checkpoint(CHECKPOINT_FILE, checkpoint)

    async def extraer_tweets(self, minimum_tweets, exporters, nonrelevant_exporter=None):
        """
        Extrae tweets hasta alcanzar el mínimo especificado.

        Args:
            minimum_tweets (int): Número mínimo de tweets a extraer
            exporters (list): Lista de exportadores para guardar los tweets
            nonrelevant_exporter: Exportador para tweets no relevantes

        Returns:
            dict: Estadísticas de la extracción
        """
        tweets = None
        consulta_actual = ""
        categoria_actual = ""
        consultas_sin_resultados = 0
        max_consultas_sin_resultados = 5

        try:
            while self.tweets_count < minimum_tweets:
                # Cambiar consulta periódicamente o si no hay resultados
                if tweets is None or random.random() < 0.3 or consultas_sin_resultados >= max_consultas_sin_resultados:
                    consulta_actual, categoria_actual = self.generar_consulta()
                    consultas_sin_resultados = 0

                try:
                    tweets = await self.obtener_tweets(tweets, consulta_actual)
                except asyncio.CancelledError:
                    # Capturar cancelación para guardar checkpoint
                    log_warning(self.logger, "Operación cancelada. Guardando checkpoint...")
                    self.guardar_checkpoint()
                    raise
                except Exception as e:
                    log_error(self.logger, f"Error al obtener tweets: {e}")
                    await asyncio.sleep(30)
                    tweets = None
                    continue

                if not tweets or len(tweets) == 0:
                    log_warning(self.logger, "No se encontraron más tweets con esta consulta.")
                    consultas_sin_resultados += 1
                    tweets = None
                    continue

                tweets_procesados = 0
                for tweet in tweets:
                    # Procesar tweet
                    procesado = self.procesar_tweet(tweet, categoria_actual, consulta_actual, exporters, nonrelevant_exporter)
                    if procesado:
                        tweets_procesados += 1

                    # Si alcanzamos el objetivo, salimos del bucle
                    if self.tweets_count >= minimum_tweets:
                        break

                # Si no procesamos ningún tweet en esta página, puede que necesitemos cambiar la consulta
                if tweets_procesados == 0:
                    consultas_sin_resultados += 1
                    if consultas_sin_resultados >= max_consultas_sin_resultados:
                        log_warning(self.logger, f"No se han encontrado tweets relevantes en {max_consultas_sin_resultados} consultas consecutivas. Cambiando estrategia...")
                        tweets = None

                # Mostrar progreso periódicamente
                if self.tweets_count % 100 == 0 and self.tweets_count > 0:
                    log_success(self.logger, f"Progreso: {self.tweets_count}/{minimum_tweets} tweets recolectados ({(self.tweets_count/minimum_tweets)*100:.1f}%)")

        except asyncio.CancelledError:
            # Capturar cancelación para guardar checkpoint
            log_warning(self.logger, "Operación cancelada por el usuario. Guardando checkpoint...")
            self.guardar_checkpoint()
            raise
        finally:
            # Guardar checkpoint final
            self.guardar_checkpoint()

        # Retornar estadísticas
        return {
            'tweets_count': self.tweets_count,
            'tweets_personales': self.tweets_personales,
            'tweets_filtrados': self.tweets_filtrados,
            'estadisticas': self.estadisticas
        }

    def mostrar_estadisticas(self, estadisticas):
        """
        Muestra estadísticas de la extracción.

        Args:
            estadisticas (dict): Estadísticas a mostrar
        """
        print(f"\n{Back.BLUE}{Fore.WHITE}═══════════════════════════════════════════════════════════════════════{Style.RESET_ALL}")
        print(f"{Back.BLUE}{Fore.YELLOW}                      ESTADÍSTICAS DE RECOLECCIÓN                      {Style.RESET_ALL}")
        print(f"{Back.BLUE}{Fore.WHITE}═══════════════════════════════════════════════════════════════════════{Style.RESET_ALL}")

        print(f"{Fore.WHITE}Total de tweets recolectados: {Fore.GREEN}{estadisticas['tweets_count']}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Expresiones personales identificadas: {Fore.GREEN}{estadisticas['tweets_personales']}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Tweets filtrados (no relevantes): {Fore.YELLOW}{estadisticas['tweets_filtrados']}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Tweets únicos procesados: {Fore.GREEN}{len(self.tweet_ids_procesados)}{Style.RESET_ALL}")

        print(f"\n{Fore.YELLOW}Distribución por categorías:{Style.RESET_ALL}")
        for categoria, cantidad in estadisticas['estadisticas'].items():
            if cantidad > 0:
                print(f"{Fore.GREEN}• {categoria}: {cantidad} tweets{Style.RESET_ALL}")

        print(f"{Back.BLUE}{Fore.WHITE}═══════════════════════════════════════════════════════════════════════{Style.RESET_ALL}")