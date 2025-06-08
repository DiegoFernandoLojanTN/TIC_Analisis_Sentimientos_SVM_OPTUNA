"""
Módulo de utilidades para el Twitter Scraper.
Contiene funciones auxiliares para logging, manejo de errores, etc.
"""
import logging
import json
import os
import time
import random
import asyncio
from datetime import datetime
from pathlib import Path
import backoff
from colorama import init, Fore, Style, Back
from tqdm import tqdm

from config.settings import (
    MIN_PAUSE, MAX_PAUSE, LONG_PAUSE_PROB,
    LONG_PAUSE_MIN, LONG_PAUSE_MAX
)

# Inicializar colorama para mensajes de consola coloridos
init(autoreset=True)

# Configuración del logger
def setup_logger(log_file, log_level="INFO"):
    """
    Configura el sistema de logging para la aplicación.

    Args:
        log_file (str): Ruta al archivo de log
        log_level (str): Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        logging.Logger: Objeto logger configurado
    """
    # Crear directorio de logs si no existe
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configurar logger
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    # Formato del log
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Configurar logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger('twitter_scraper')

# Funciones para mensajes en consola
def print_banner():
    """Imprime un banner de inicio para el script"""
    banner = f"""
{Back.BLUE}{Fore.WHITE}╔═══════════════════════════════════════════════════════════════════════╗
{Back.BLUE}{Fore.YELLOW}║                     TWITTER SCRAPER - CRISIS ENERGÉTICA                {Back.BLUE}{Fore.WHITE}║
{Back.BLUE}{Fore.GREEN}║                       Análisis de Estrés en Ecuador                     {Back.BLUE}{Fore.WHITE}║
{Back.BLUE}{Fore.WHITE}╚═══════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)

def log_info(logger, mensaje, console=True):
    """
    Registra un mensaje informativo en el log y opcionalmente en consola.

    Args:
        logger (logging.Logger): Logger configurado
        mensaje (str): Mensaje a registrar
        console (bool): Si es True, también imprime en consola con formato
    """
    logger.info(mensaje)
    if console:
        print(f"{Fore.BLUE}[INFO] {mensaje}{Style.RESET_ALL}")

def log_success(logger, mensaje, console=True):
    """
    Registra un mensaje de éxito en el log y opcionalmente en consola.

    Args:
        logger (logging.Logger): Logger configurado
        mensaje (str): Mensaje a registrar
        console (bool): Si es True, también imprime en consola con formato
    """
    logger.info(f"SUCCESS: {mensaje}")
    if console:
        print(f"{Fore.GREEN}[ÉXITO] {mensaje}{Style.RESET_ALL}")

def log_warning(logger, mensaje, console=True):
    """
    Registra un mensaje de advertencia en el log y opcionalmente en consola.

    Args:
        logger (logging.Logger): Logger configurado
        mensaje (str): Mensaje a registrar
        console (bool): Si es True, también imprime en consola con formato
    """
    logger.warning(mensaje)
    if console:
        print(f"{Fore.YELLOW}[ADVERTENCIA] {mensaje}{Style.RESET_ALL}")

def log_error(logger, mensaje, console=True):
    """
    Registra un mensaje de error en el log y opcionalmente en consola.

    Args:
        logger (logging.Logger): Logger configurado
        mensaje (str): Mensaje a registrar
        console (bool): Si es True, también imprime en consola con formato
    """
    logger.error(mensaje)
    if console:
        print(f"{Fore.RED}[ERROR] {mensaje}{Style.RESET_ALL}")

# Funciones para manejo de checkpoints
def save_checkpoint(checkpoint_file, data):
    """
    Guarda un punto de control para poder reanudar la recolección.

    Args:
        checkpoint_file (str): Ruta al archivo de checkpoint
        data (dict): Datos a guardar en el checkpoint
    """
    # Crear directorio si no existe
    checkpoint_dir = os.path.dirname(checkpoint_file)
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)

    try:
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Error al guardar checkpoint: {e}{Style.RESET_ALL}")
        return False

def load_checkpoint(checkpoint_file):
    """
    Carga un punto de control para reanudar la recolección.

    Args:
        checkpoint_file (str): Ruta al archivo de checkpoint

    Returns:
        dict: Datos del checkpoint o None si no existe
    """
    if not os.path.exists(checkpoint_file):
        return None

    try:
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None

# Funciones para manejo de reintentos
def backoff_hdlr(details):
    """
    Manejador para backoff que registra información sobre reintentos.

    Args:
        details (dict): Detalles del reintento
    """
    print(f"{Fore.YELLOW}[REINTENTO] Intento {details['tries']} fallido. Esperando {details['wait']:.2f} segundos antes del siguiente intento.{Style.RESET_ALL}")

# Simulación de comportamiento humano
async def simulate_human_behavior():
    """
    Simula comportamiento humano para evitar detección como bot.
    Introduce pausas aleatorias y variaciones en el tiempo de respuesta.
    """
    # Pausa aleatoria entre valores configurados
    pause_time = random.uniform(MIN_PAUSE, MAX_PAUSE)
    await asyncio.sleep(pause_time)

    # Ocasionalmente hacer pausas más largas según probabilidad configurada
    if random.random() < LONG_PAUSE_PROB:
        long_pause = random.uniform(LONG_PAUSE_MIN, LONG_PAUSE_MAX)
        await asyncio.sleep(long_pause)

# Clase para barra de progreso
class ProgressTracker:
    """Clase para seguimiento de progreso con barra visual."""

    def __init__(self, total, desc="Progreso"):
        """
        Inicializa el seguimiento de progreso.

        Args:
            total (int): Total de elementos a procesar
            desc (str): Descripción de la barra de progreso
        """
        self.total = total
        self.desc = desc
        self.progress_bar = tqdm(
            total=total,
            desc=f"{Fore.CYAN}{desc}{Style.RESET_ALL}",
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            colour='green'
        )
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.update_interval = 60  # Actualizar estadísticas cada 60 segundos

    def update(self, increment=1):
        """
        Actualiza el progreso.

        Args:
            increment (int): Cantidad a incrementar
        """
        self.current += increment
        self.progress_bar.update(increment)

        # Mostrar estadísticas periódicamente
        current_time = time.time()
        if current_time - self.last_update_time >= self.update_interval:
            self.show_stats()
            self.last_update_time = current_time

    def show_stats(self):
        """Muestra estadísticas de velocidad y tiempo estimado."""
        elapsed = time.time() - self.start_time
        if self.current > 0 and elapsed > 0:
            rate = self.current / elapsed
            remaining = (self.total - self.current) / rate if rate > 0 else 0

            # Formatear tiempo restante
            hours, remainder = divmod(remaining, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_remaining = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

            print(f"{Fore.CYAN}[ESTADÍSTICAS] Velocidad: {rate:.2f} tweets/segundo. Tiempo restante estimado: {time_remaining}{Style.RESET_ALL}")

    def close(self):
        """Cierra la barra de progreso."""
        self.progress_bar.close()

        # Mostrar estadísticas finales
        elapsed = time.time() - self.start_time
        if self.current > 0 and elapsed > 0:
            rate = self.current / elapsed

            # Formatear tiempo total
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_elapsed = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

            print(f"{Fore.GREEN}[COMPLETADO] Recolectados {self.current} tweets en {time_elapsed} ({rate:.2f} tweets/segundo){Style.RESET_ALL}")