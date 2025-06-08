"""
Configuraciones del crawler de Twitter para el análisis del estrés
durante la crisis energética en Ecuador.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Cargar coordenadas
def cargar_coordenadas():
    """Carga las coordenadas desde el archivo JSON."""
    try:
        with open('datosjson/provincias.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data['provincias'][0]['coordenadas']
    except Exception as e:
        print(f"Error al cargar coordenadas: {e}")
        return []

# Credenciales
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')

# Fechas de búsqueda
START_DATE = os.getenv('START_DATE', '2024-01-01')
END_DATE = os.getenv('END_DATE', '2024-12-31')

# Configuraciones de búsqueda y rendimiento
MAX_TWEETS = int(os.getenv('MAX_TWEETS', 5000))
SCROLL_PAUSE_TIME = 1.0
RETRY_COUNT = 5
BATCH_SIZE = 50

# Configuraciones de geolocalización
COORDENADAS = cargar_coordenadas()
RADIO_BUSQUEDA = "100km"

# Hashtags principales relacionados con la crisis y el estrés
CRISIS_HASHTAGS = [
    'CrisisEnergeticaEcuador',
    'ApagonEcuador',
    'EstresCortes',
    'CortesLuzEcuador',
    'EcuadorSinLuz',
    'CrisisElectricaEC',
    'ApagonesEcuador',
    'EcuadorCrisis',
    'EstresApagon',
    'EstresElectrico',
    'CrisisLuzEcuador',
    'SinLuzEcuador',
    'ApagonEC',
    'EmergenciaEnergeticaEC',
    'EmergenciaElectricaEcuador'
]

# Palabras clave organizadas por categorías según el análisis psicológico
KEYWORDS = [
    # Estrés Directo
    'estresado', 'estresada', 'estresante', 'tensionado', 'tensionada',
    'tenso', 'tensa', 'agotado', 'agotada', 'agotamiento',
    'saturado', 'saturada', 'presionado', 'presionada',

    # Manifestaciones Físicas
    'cansado', 'cansada', 'agobiado', 'agobiada', 'exhausto',
    'exhausta', 'fatigado', 'fatigada', 'sin dormir', 'insomnio',
    'desvelado', 'desvelada', 'sin energía', 'agotamiento físico',

    # Manifestaciones Psicológicas
    'preocupado', 'preocupada', 'inquieto', 'inquieta',
    'frustrado', 'frustrada', 'irritado', 'irritada',
    'desesperado', 'desesperada', 'ansioso', 'ansiosa',
    'sin concentración', 'desenfocado', 'desenfocada',

    # Impacto en Actividades
    'no puedo trabajar', 'sin poder trabajar', 'no puedo estudiar',
    'sin poder estudiar', 'improductivo', 'improductiva',
    'retrasado', 'retrasada', 'perdiendo clases', 'perdiendo trabajo',

    # Expresiones de Malestar
    'no aguanto', 'insoportable', 'hartazgo', 'harto', 'harta',
    'colapsado', 'colapsada', 'vulnerable', 'afectado', 'afectada',
    'esto es el colmo', 'hasta cuando'
]

# Frases de búsqueda compuestas usando modificadores y contexto
SEARCH_PHRASES = [
    # Combinaciones con contexto Ecuador
    'Ecuador AND apagón AND estresado',
    'Ecuador AND "crisis energética" AND agotado',
    'Ecuador AND "sin luz" AND frustrado',
    'Ecuador AND apagones AND insomnio',
    'ecuatoriano AND "cortes de luz" AND estresado',
    'ecuatoriana AND "sin electricidad" AND preocupada',

    # Combinaciones con modificadores
    'muy estresado AND apagones AND Ecuador',
    'demasiado cansado AND "crisis energética" AND Ecuador',
    'bastante frustrado AND "cortes de luz" AND Ecuador',
    'extremadamente agotado AND apagones AND Ecuador',
    'totalmente colapsado AND "sin luz" AND Ecuador',

    # Frases con CELEC y ministerio
    'CELEC AND estresado AND apagones',
    'CELEC AND frustrado AND "crisis energética"',
    '"ministerio de energía" AND estresado AND Ecuador',
    '"sector eléctrico ecuatoriano" AND preocupado',

    # Combinaciones de manifestaciones físicas y psicológicas
    'insomnio AND apagones AND Ecuador',
    'sin concentración AND "cortes de luz" AND Ecuador',
    'agotamiento físico AND "crisis energética" AND Ecuador',
    'ansiedad AND apagones AND Ecuador',

    # Impacto en actividades
    '"no puedo trabajar" AND apagones AND Ecuador',
    '"sin poder estudiar" AND "cortes de luz" AND Ecuador',
    'improductivo AND "crisis energética" AND Ecuador',
    '"perdiendo clases" AND apagones AND Ecuador'
]

# Configuraciones del sistema
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'data/output/tweets')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
CHECKPOINT_DIR = 'data/checkpoints'

# Crear directorios necesarios
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CHECKPOINT_DIR, exist_ok=True)

def get_output_filename(coordenada: tuple, termino_busqueda: str, fecha: str = None) -> str:
    """
    Genera nombre de archivo basado en coordenada, término y fecha.
    
    Args:
        coordenada: Tupla (lat, lon)
        termino_busqueda: Término de búsqueda
        fecha: Fecha en formato YYYY-MM-DD (opcional)
    
    Returns:
        str: Nombre del archivo formateado
    """
    lat, lon = coordenada
    if fecha is None:
        fecha = START_DATE
    
    fecha_str = datetime.strptime(fecha, '%Y-%m-%d').strftime('%B_%Y')
    termino_limpio = termino_busqueda.replace(' ', '_').replace('"', '').replace('AND', '_')
    
    return os.path.join(
        OUTPUT_DIR,
        f"tweets_{fecha_str}_{termino_limpio}_lat{lat}_lon{lon}.csv"
    )

# Columnas para el CSV de salida
CSV_COLUMNS = [
    'tweet_id',
    'autor',
    'nombre_completo',
    'contenido',
    'fecha_publicacion',
    'retweets',
    'likes',
    'hashtags',
    'vistas',
    'comentarios',
    'guardados',
    'hashtags_encontrados',
    'url_tweet',
    'termino_busqueda',
    'coordenada_lat',
    'coordenada_lon',
    'sentimiento',
    'categoria_estres'
]

# Configuraciones del WebDriver optimizadas
WEBDRIVER_SETTINGS = {
    'headless': os.getenv('USE_HEADLESS', 'True').lower() == 'true',  # Ejecuta el navegador en modo sin interfaz si la variable de entorno lo indica
    'implicit_wait': 5,  # Espera implícita de 5 segundos para encontrar elementos en la página
    'page_load_timeout': 30,  # Tiempo máximo de espera para cargar una página (30 segundos)
    'scroll_increment': 800,  # Cantidad de píxeles que se desplaza cada vez hacia abajo al hacer scroll
    'max_retries': 3,  # Número máximo de reintentos ante fallos de carga o scroll
    'min_scroll_pause': 0.5,  # Pausa mínima entre desplazamientos para simular comportamiento humano
    'max_scroll_pause': 1.5  # Pausa máxima entre desplazamientos para simular comportamiento humano
}

# Configuraciones de extracción
EXTRACTION_SETTINGS = {
    'tweets_por_lote': 50,  # Número de tweets a procesar por cada lote de extracción
    'max_intentos_scroll': 5,  # Intentos máximos de scroll antes de detener la búsqueda por término
    'pausa_entre_terminos': 10,  # Pausa en segundos entre la extracción de distintos términos de búsqueda
    'max_tweets_por_termino': 500  # Límite máximo de tweets a recolectar por cada término de búsqueda
}
