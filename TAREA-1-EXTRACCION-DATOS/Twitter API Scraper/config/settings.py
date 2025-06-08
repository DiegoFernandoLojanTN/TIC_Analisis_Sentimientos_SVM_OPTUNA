"""
Configuraciones generales para el Twitter Scraper.
Contiene rutas, credenciales y parámetros de configuración.
"""
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Directorios de datos
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
NONRELEVANT_DIR = os.path.join(DATA_DIR, "nonrelevant")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
CHECKPOINTS_DIR = os.path.join(DATA_DIR, "checkpoints")

# Asegurar que los directorios existan
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(NONRELEVANT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(CHECKPOINTS_DIR, exist_ok=True)

# Archivos de configuración
LOG_FILE = os.path.join(LOGS_DIR, f"scraper_{datetime.now().strftime('%Y%m%d')}.log")
CHECKPOINT_FILE = os.path.join(CHECKPOINTS_DIR, "last_checkpoint.json")
COOKIES_FILE = os.path.join(DATA_DIR, "twitter_cookies.json") 

# Credenciales de Twitter (se cargarán desde .env)
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME", "")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD", "")
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL", "")
TWITTER_PHONE = os.getenv("TWITTER_PHONE", "")

# Parámetros de búsqueda
# Por defecto, buscar tweets desde marzo 2024 hasta diciembre 2024
DEFAULT_START_DATE = datetime(2024, 3, 1)  # Desde el 1 de marzo de 2024
DEFAULT_END_DATE = datetime(2024, 12, 31)  # Hasta el 31 de diciembre de 2024

# Fechas de búsqueda (formato YYYY-MM-DD)
DATE_START = os.getenv("DATE_START", DEFAULT_START_DATE.strftime('%Y-%m-%d'))
DATE_END = os.getenv("DATE_END", DEFAULT_END_DATE.strftime('%Y-%m-%d'))

# Número mínimo de tweets a recolectar (objetivo entre 5K y 10K)
try:
    minimum_tweets_value = os.getenv("MINIMUM_TWEETS", "10000")
    # Eliminar cualquier comentario que pueda estar en la misma línea
    if '#' in minimum_tweets_value:
        minimum_tweets_value = minimum_tweets_value.split('#')[0].strip()
    MINIMUM_TWEETS = int(minimum_tweets_value)
except ValueError:
    # Si hay un error, usar un valor predeterminado
    MINIMUM_TWEETS = 10000
    print("Advertencia: No se pudo leer MINIMUM_TWEETS del archivo .env, usando valor predeterminado 10000")

# Configuración de reintentos
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "5"))
RETRY_DELAY = float(os.getenv("RETRY_BASE_DELAY", "30"))  # segundos

# Configuración de comportamiento humano
MIN_PAUSE = float(os.getenv("MIN_PAUSE", "1.5"))  # segundos
MAX_PAUSE = float(os.getenv("MAX_PAUSE", "5.0"))  # segundos
LONG_PAUSE_PROB = float(os.getenv("LONG_PAUSE_PROB", "0.1"))  # probabilidad de pausa larga
LONG_PAUSE_MIN = float(os.getenv("LONG_PAUSE_MIN", "8.0"))  # segundos
LONG_PAUSE_MAX = float(os.getenv("LONG_PAUSE_MAX", "15.0"))  # segundos

# Configuración de detección de bloqueos
BLOCK_WAIT_MIN = int(os.getenv("BLOCK_WAIT_MIN", "60"))  # 1 minuto
BLOCK_WAIT_MAX = int(os.getenv("BLOCK_WAIT_MAX", "1200"))  # 20 minuto