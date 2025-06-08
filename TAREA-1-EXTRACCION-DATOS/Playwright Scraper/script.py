import nest_asyncio
import asyncio
import re
import random
import pandas as pd
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from tqdm import tqdm
import os
import unicodedata
from pathlib import Path
import time
import signal
import sys

# ==============================================
# CONFIGURACIÓN INICIAL
# ==============================================

nest_asyncio.apply()

# Configuración de directorios
SCRIPT_DIR = Path(__file__).parent.absolute()
SESSION_DIR = SCRIPT_DIR / "twitter_session"
SESSION_DIR.mkdir(exist_ok=True)
DATA_DIR = SCRIPT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Configuración de tiempos (en segundos)
CONFIG = {
    'timeouts': {
        'page_load': 60,
        'element_wait': 40,  # Aumentado para Top/Latest
        'inactivity': 300,
        'login': 180
    },
    'delays': {
        'scroll': (2, 5),  # Más aleatoriedad
        'long_break': (60, 120),  # Pausas más largas
        'retry': 30,
        'between_keywords': (30, 50)
    },
    'limits': {
        'min_tweets_per_keyword': 300,
        'max_tweets_per_keyword': 500,
        'max_retries': 3,  # Reducido para cambiar rápido de keyword
        'batch_size': 50,
        'tweets_before_long_break': 75
    }
}

# ==============================================
# PALABRAS CLAVE MEJORADAS (ESTRÉS)
# ==============================================

KEYWORDS = {
    "estres_general": [
        # Términos directos
        "estrés", "estresado", "estresada", "estresante", 
        "agobio", "agobiado", "agobiada", "sobrecargado",
        "tensionado", "tensionada", "tenso", "tensa",
        "agotado", "agotada", "agotamiento", "saturado", 
        "saturada", "presionado", "presionada",
        
        # Manifestaciones físicas
        "cansado", "cansada", "exhausto", "exhausta",
        "fatigado", "fatigada", "sin dormir", "insomnio",
        "desvelado", "desvelada", "sin energía", "agotamiento físico",
        "reventado",
        
        # Manifestaciones psicológicas
        "preocupado", "preocupada", "inquieto", "inquieta",
        "frustrado", "frustrada", "irritado", "irritada",
        "desesperado", "desesperada", "ansioso", "ansiosa",
        "sin concentración", "desenfocado", "desenfocada",
        "vulnerable",
        
        # Impacto en actividades
        "no puedo trabajar", "sin poder trabajar", 
        "no puedo estudiar", "sin poder estudiar",
        "improductivo", "improductiva", "retrasado", "retrasada",
        "perdiendo clases", "perdiendo trabajo",
        
        # Expresiones coloquiales
        "no aguanto más", "estoy hasta aquí", "no doy más",
        "esto me supera", "al borde del colapso", "quiero escapar",
        "no soporto esto", "me tiene podrido", "qué fastidio",
        "estoy hasta la madre", "ya no puedo", "es demasiado",
        "esto es el colmo", "hasta cuando", "insoportable",
        "hartazgo", "harto", "harta", "colapsado", "colapsada",
        "afectado", "afectada",
        
        # Wildcards y variaciones
        "no aguanto * trabajo", "es tanto el estrés", "tanto estrés *",
        "* me estresa", "estrés * vida", "* me tiene agobiado"
    ]
}

# Términos para excluir usuarios no deseados (ampliado)
CUENTAS_EXCLUIR = [
    "bot", "consultor", "psicólogo", "psicologo", "coach", "terapeuta",
    "asesor", "médico", "doctor", "clínica", "salud", "bienestar",
    "ayuda", "servicio", "profesional", "experto", "especialista",
    "terapia", "psicología", "mental", "emocional", "mindfulness",
    "meditación", "relajación", "autoayuda", "motivación", "inspiración",
    "empresa", "corporativo", "instituto", "fundación", "asociación",
    "consultora", "universidad", "escuela", "academia", "capacitación",
    "formación", "taller", "seminario", "webinar", "conferencia",
    "marca", "producto", "emprendimiento", "negocio", "venta",
    "publicidad", "marketing", "promoción", "sponsor", "patrocinio"
]

# Medios de Ecuador (ampliado)
MEDIOS_ECUADOR = [
    "elcomercio", "eluniverso", "ecuavisa", "teleamazonas", "primicias",
    "lahora", "expreso", "eltelegrafo", "ecuadorinmediato", "andes",
    "vistazo", "planv", "metroecuador", "tcnoticias", "gamavision",
    "canal1", "ecuadoradio", "radiohuancavilca", "radiolacalle",
    "radioquinto", "radioamazonica", "radiosucre", "radiofrance",
    "radiosuperior", "radiochocolate", "radioformula", "radiohuancavilca",
    "diarioextra", "ultimasnoticias", "revistavance", "revistacontinental",
    "revistafamilia", "revistamundo", "revistalideres", "revistacriterios"
]

ECUADOR_GEO = "geocode:-1.831239,-78.183406,500km"
DATE_RANGE = "since:2024-04-28 until:2024-12-20"

# ==============================================
# FUNCIONES AUXILIARES MEJORADAS
# ==============================================

def clean_text(text):
    """Limpieza avanzada de texto para análisis de sentimientos"""
    if not isinstance(text, str):
        return ""
    
    # Normalización y conversión a minúsculas
    text = unicodedata.normalize('NFKC', text).lower()
    
    # Eliminación de emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # símbolos & pictogramas
        u"\U0001F680-\U0001F6FF"  # transporte & símbolos
        u"\U0001F1E0-\U0001F1FF"  # banderas (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub('', text)
    
    # Patrones de limpieza
    patterns = [
        r'@\w+',                  # Menciones
        r'http[s]?://\S+',        # URLs
        r'www\.\S+',              # URLs sin http
        r'#\w+',                  # Hashtags
        r'^RT[\s:]',              # Retweets
        r'[\'\"“”‘’]',            # Comillas
        r'[\(\)\[\]\{\}<>]',      # Caracteres especiales
        r'[^\w\sáéíóúñüÁÉÍÓÚÑÜ,.;:¿?¡!\-\—]',  # Caracteres no permitidos
        r'\b\w{1,2}\b',           # Palabras muy cortas
        r'\s+',                   # Múltiples espacios
        r'[\*\/\\\#\$\%\&\+\=\|]' # Símbolos especiales
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, ' ', text)
    
    # Limpieza final
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def should_exclude_user(username):
    """Determina si el usuario debe ser excluido con filtros mejorados"""
    if not username:
        return True
    
    username_clean = username.lower()
    
    # Excluir medios y cuentas institucionales
    if any(medio in username_clean for medio in MEDIOS_ECUADOR):
        return True
    
    # Excluir cuentas de profesionales/spam
    if any(termino in username_clean for termino in CUENTAS_EXCLUIR):
        return True
    
    # Excluir por terminaciones comunes de bots/instituciones
    if username_clean.endswith(("ec", "com", "net", "org", "bot", "official")):
        return True
    
    return False

async def save_batch_to_csv(batch, file_path):
    """Guarda un lote de tweets en CSV con manejo de errores mejorado"""
    try:
        if not batch:
            return True
            
        df = pd.DataFrame(batch)
        
        # Verificar duplicados en el batch actual
        df.drop_duplicates(subset=['tweet_limpio', 'fecha'], inplace=True)
        
        write_header = not file_path.exists()
        df.to_csv(file_path, mode='a', header=write_header, index=False, encoding='utf-8-sig')
        return True
    except Exception as e:
        print(f"❌ Error guardando lote: {str(e)}")
        return False

def signal_handler(sig, frame):
    """Maneja la señal CTRL+C para una salida limpia"""
    print('\n\n🛑 Script detenido por el usuario. Guardando datos recolectados...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def get_csv_path():
    """Genera la ruta del archivo CSV único con timestamp"""
    return DATA_DIR / f"tweets_estres_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

def load_existing_tweets(file_path):
    """Carga tweets existentes para evitar duplicados entre sesiones"""
    if not file_path.exists():
        return set()
    
    try:
        df = pd.read_csv(file_path)
        return set(
            hash(row['tweet_limpio'] + str(row['fecha'])) 
            for _, row in df.iterrows() 
            if pd.notna(row['tweet_limpio']) and pd.notna(row['fecha'])
        )
    except Exception as e:
        print(f"⚠️ Error cargando tweets existentes: {str(e)}")
        return set()

# ==============================================
# CORE DEL SCRAPER 
# ==============================================

class TwitterScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.current_keyword = ""
        self.tweets_collected = 0
        self.last_activity = datetime.now()
        self.should_stop = False
        self.csv_path = get_csv_path()
        self.seen_tweets = load_existing_tweets(self.csv_path)
        self.search_modes = ['live', 'top']  # Alternar entre Latest y Top
        
    async def initialize_browser(self):
        """Inicializa el navegador con configuración persistente"""
        try:
            print("\n🖥️ Inicializando navegador...")
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch_persistent_context(
                str(SESSION_DIR),
                headless=False,
                timeout=CONFIG['timeouts']['page_load'] * 1000,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized"
                ],
                viewport={"width": 1280, "height": 720},
                accept_downloads=True,
                locale="es-EC",
                geolocation={"latitude": -1.831239, "longitude": -78.183406},
                permissions=["geolocation"]
            )
            self.page = await self.browser.new_page()
            await self.page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept-Language": "es-EC,es;q=0.9"
            })
            print("✅ Navegador listo")
            return True
        except Exception as e:
            print(f"❌ Error inicializando navegador: {str(e)}")
            return False

    async def search_keyword(self, keyword, mode='live'):
        """Realiza búsqueda de un keyword específico en modo Top o Latest"""
        self.current_keyword = keyword
        search_url = (
            f"https://twitter.com/search?q={keyword.replace(' ', '%20')} "
            f"{DATE_RANGE} {ECUADOR_GEO}&src=typed_query&f={mode}"
        )
        
        try:
            print(f"\n🔍 Buscando: '{keyword}' (Modo: {'Latest' if mode == 'live' else 'Top'})")
            await self.page.goto(search_url, timeout=CONFIG['timeouts']['page_load'] * 1000)
            
            if "login" in self.page.url.lower():
                print("\n⚠️ Requiere autenticación manual")
                print("Por favor inicia sesión en la ventana del navegador y presiona Enter aquí cuando termines")
                input(">>> Presiona Enter después de iniciar sesión <<<")
                await self.page.goto(search_url, timeout=CONFIG['timeouts']['login'] * 1000)
            
            return True
        except Exception as e:
            print(f"❌ Error en búsqueda: {str(e)}")
            return False

    async def extract_tweets(self):
        """Extrae tweets con manejo robusto de errores y evita duplicados"""
        tweets_buffer = []
        retry_count = 0
        last_count = 0
        same_count_attempts = 0
        current_mode = 0  # Alternar entre Latest (0) y Top (1)
        
        min_tweets = CONFIG['limits']['min_tweets_per_keyword']
        max_tweets = CONFIG['limits']['max_tweets_per_keyword']
        target_tweets = random.randint(min_tweets, max_tweets)
        
        progress = tqdm(
            total=target_tweets,
            desc=f"📊 Recolectando '{self.current_keyword[:20]}...'",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} tweets [{elapsed}<{remaining}]",
            colour='green'
        )
        
        while (len(tweets_buffer) < target_tweets and 
               retry_count < CONFIG['limits']['max_retries'] and 
               not self.should_stop):
            
            try:
                # Alternar entre modos de búsqueda cada 2 reintentos
                if retry_count > 0 and retry_count % 2 == 0:
                    current_mode = 1 - current_mode  # Alternar entre 0 y 1
                    if not await self.search_keyword(self.current_keyword, self.search_modes[current_mode]):
                        retry_count += 1
                        continue
                
                if (datetime.now() - self.last_activity).seconds > CONFIG['timeouts']['inactivity']:
                    print("\n⚡ Reiniciando por inactividad...")
                    await self.page.reload()
                    self.last_activity = datetime.now()
                    retry_count += 1
                    await asyncio.sleep(CONFIG['delays']['retry'])
                    continue
                
                await self.page.wait_for_selector("article", timeout=CONFIG['timeouts']['element_wait'] * 1000)
                tweet_elements = await self.page.query_selector_all("article")
                
                if len(tweet_elements) == 0:
                    print("\n⚠️ No se encontraron tweets, reintentando...")
                    retry_count += 1
                    await asyncio.sleep(CONFIG['delays']['retry'])
                    continue
                
                new_tweets_found = 0
                
                for tweet in tweet_elements:
                    try:
                        content = await tweet.query_selector("div[data-testid='tweetText']")
                        if not content:
                            continue
                            
                        raw_text = await content.inner_text()
                        text = clean_text(raw_text)
                        
                        if not text or len(text) < 20:  # Aumentado mínimo de caracteres
                            continue
                        
                        # Crear un hash único del tweet
                        date_element = await tweet.query_selector("time")
                        date_str = await date_element.get_attribute("datetime") if date_element else ""
                        tweet_hash = hash(text + date_str)
                        
                        # Verificar si el tweet ya fue procesado
                        if tweet_hash in self.seen_tweets:
                            continue
                            
                        self.seen_tweets.add(tweet_hash)
                        
                        user_element = await tweet.query_selector("div[data-testid='User-Name']")
                        username = (await user_element.inner_text()).split("\n")[0] if user_element else None
                        
                        if should_exclude_user(username):
                            continue
                            
                        tweet_date = datetime.fromisoformat(date_str[:-1]).strftime("%Y-%m-%d") if date_str else None
                        
                        tweet_data = {
                            "keyword": self.current_keyword,
                            "usuario": username,
                            "fecha": tweet_date,
                            "tweet": raw_text,
                            "tweet_limpio": text,
                            "categoria": next((k for k, v in KEYWORDS.items() if self.current_keyword in v), "otros"),
                            "extraccion": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "modo_busqueda": self.search_modes[current_mode]
                        }
                        
                        tweets_buffer.append(tweet_data)
                        new_tweets_found += 1
                        self.last_activity = datetime.now()
                        progress.update(1)
                        
                        if len(tweets_buffer) % CONFIG['limits']['batch_size'] == 0:
                            if not await save_batch_to_csv(tweets_buffer, self.csv_path):
                                retry_count += 1
                            tweets_buffer = []
                        
                        if len(tweets_buffer) % CONFIG['limits']['tweets_before_long_break'] == 0:
                            long_delay = random.randint(*CONFIG['delays']['long_break'])
                            print(f"\n⏳ Pausa de {long_delay}s para evitar detección...")
                            await asyncio.sleep(long_delay)
                        
                        if len(tweets_buffer) >= target_tweets:
                            break
                            
                    except Exception as e:
                        continue
                
                if new_tweets_found == 0:
                    same_count_attempts += 1
                    if same_count_attempts > 2:  # Reducido para cambiar más rápido
                        print(f"\n⚠️ No hay nuevos tweets únicos, cambiando modo de búsqueda... (Recolectados: {len(tweets_buffer)}/{target_tweets})")
                        current_mode = 1 - current_mode
                        if not await self.search_keyword(self.current_keyword, self.search_modes[current_mode]):
                            break
                        same_count_attempts = 0
                else:
                    same_count_attempts = 0
                
                try:
                    await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(random.uniform(*CONFIG['delays']['scroll']))
                except:
                    await self.page.reload()
                    await asyncio.sleep(CONFIG['delays']['retry'])
                    
            except Exception as e:
                print(f"\n⚠️ Error: {str(e)} - Reintentando... ({retry_count + 1}/{CONFIG['limits']['max_retries']})")
                await asyncio.sleep(CONFIG['delays']['retry'])
                retry_count += 1
                continue
        
        if tweets_buffer:
            await save_batch_to_csv(tweets_buffer, self.csv_path)
        
        progress.close()
        return len(tweets_buffer)

    async def close(self):
        """Cierra los recursos adecuadamente"""
        try:
            if hasattr(self, 'browser') and self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                await self.playwright.stop()
        except Exception as e:
            print(f"⚠️ Error al cerrar recursos: {str(e)}")

# ==============================================
# EJECUCIÓN PRINCIPAL
# ==============================================

async def main():
    print("""
    🚀 TWITTER SCRAPER - EXTRACCIÓN DE TWEETS SOBRE ESTRÉS
    📅 Rango de fechas: 28 Abril 2024 - 20 Diciembre 2024
    📍 Geolocalización: Ecuador (radio 500km)
    🔍 Palabras clave: {} términos en {} categorías
    🎯 Objetivo: {} a {} tweets por palabra clave
    📂 Archivo de salida: {}
    🛡️ Protecciones: Delays aleatorios, límites de tasa, reinicios automáticos
    🔄 Modos de búsqueda: Alternando entre Latest y Top
    """.format(
        sum(len(v) for v in KEYWORDS.values()),
        len(KEYWORDS),
        CONFIG['limits']['min_tweets_per_keyword'],
        CONFIG['limits']['max_tweets_per_keyword'],
        get_csv_path()
    ))
    
    print("⏳ Inicializando...")
    scraper = TwitterScraper()
    
    if not await scraper.initialize_browser():
        print("❌ No se pudo inicializar el navegador. Saliendo...")
        return
    
    try:
        all_keywords = [kw for sublist in KEYWORDS.values() for kw in sublist]
        random.shuffle(all_keywords)
        total_keywords = len(all_keywords)
        processed = 0
        total_tweets = 0
        
        print(f"\n🔍 Comenzando búsqueda de {total_keywords} términos...")
        start_total = datetime.now()
        
        for keyword in all_keywords:
            processed += 1
            start_time = datetime.now()
            
            if not await scraper.search_keyword(keyword):
                continue
                
            count = await scraper.extract_tweets()
            total_tweets += count
            elapsed = datetime.now() - start_time
            
            print(f"\n✅ [{processed}/{total_keywords}] '{keyword}': {count} tweets | Tiempo: {elapsed}")
            print(f"📊 Total acumulado: {total_tweets} tweets")
            
            if keyword != all_keywords[-1]:
                delay = random.randint(*CONFIG['delays']['between_keywords'])
                print(f"⏳ Esperando {delay}s antes del siguiente término...")
                await asyncio.sleep(delay)
                
        total_time = datetime.now() - start_total
        print(f"\n🎉 Proceso completado!")
        print(f"⏱️ Tiempo total: {total_time}")
        print(f"📊 Total de tweets recolectados: {total_tweets}")
        print(f"📁 Datos guardados en: {scraper.csv_path}")
        
    except Exception as e:
        print(f"\n🔥 Error crítico: {str(e)}")
    finally:
        await scraper.close()

if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        nest_asyncio.apply()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Script detenido manualmente por el usuario")
        sys.exit(0)
    finally:
        print("\n" + "="*60)
        print("Gracias por usar el Twitter Scraper - Análisis de Estrés")
        print("="*60 + "\n")