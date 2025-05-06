"""
Script principal para la extracción de tweets relacionados con el estrés
durante la crisis energética en Ecuador.

Este script orquesta el proceso completo de extracción, utilizando
coordenadas geográficas para un análisis más preciso por región.
"""

import sys
import time
from datetime import datetime
from src.utils.logger import logger
from src.utils.webdriver import setup_web_driver
from src.crawler.tweet_scraper import TweetScraper
from config.settings import (
    CRISIS_HASHTAGS,
    KEYWORDS,
    SEARCH_PHRASES,
    COORDENADAS,
    EXTRACTION_SETTINGS
)

def mostrar_resumen_configuracion():
    """Muestra un resumen de la configuración actual."""
    logger.info("""
    Configuración de extracción:
    ---------------------------
    - Total términos de búsqueda: {}
    - Total coordenadas: {}
    - Tweets máximos por término: {}
    - Radio de búsqueda: 100km
    """.format(
        len(CRISIS_HASHTAGS + KEYWORDS + SEARCH_PHRASES),
        len(COORDENADAS),
        EXTRACTION_SETTINGS['max_tweets_por_termino']
    ))

def procesar_termino(scraper, termino: str, coordenada: tuple) -> bool:
    """
    Procesa un término de búsqueda para una coordenada específica.

    Args:
        scraper: Instancia de TweetScraper
        termino: Término de búsqueda
        coordenada: Tupla (lat, lon) para la búsqueda

    Returns:
        bool: True si la extracción fue exitosa
    """
    try:
        logger.info(f"""
        Iniciando búsqueda:
        - Término: {termino}
        - Coordenadas: ({coordenada[0]}, {coordenada[1]})
        """)

        tweets = scraper.extraer_tweets(
            termino_busqueda=termino,
            coordenada=coordenada,
            max_tweets=EXTRACTION_SETTINGS['max_tweets_por_termino'],
            continuar_anterior=True
        )

        if tweets:
            logger.info(f"Encontrados {len(tweets)} tweets para '{termino}' en coordenada {coordenada}")
            return True
        else:
            logger.warning(f"No se encontraron tweets para '{termino}' en coordenada {coordenada}")
            return False

    except Exception as e:
        logger.error(f"Error procesando término '{termino}' en coordenada {coordenada}: {str(e)}")
        return False

def mostrar_estadisticas_finales(fecha_inicio: datetime, coordenadas: int, terminos: int, tweets: int):
    """
    Muestra las estadísticas finales del proceso.

    Args:
        fecha_inicio: Fecha y hora de inicio del proceso
        coordenadas: Número de coordenadas procesadas
        terminos: Número de términos procesados
        tweets: Total de tweets encontrados
    """
    duracion = datetime.now() - fecha_inicio
    logger.info(f"""
    Estadísticas finales:
    --------------------
    Duración total: {duracion}
    Coordenadas procesadas: {coordenadas}/{len(COORDENADAS)}
    Términos procesados: {terminos}
    Total tweets encontrados: {tweets}

    Archivos generados:
    ------------------
    - Tweets: data/output/tweets/
    - Checkpoints: data/checkpoints/
    - Logs: logs/
    """)

def main():
    """Función principal del crawler."""
    fecha_inicio = datetime.now()
    logger.info("Iniciando proceso de extracción de tweets")
    mostrar_resumen_configuracion()

    try:
        # Configurar el WebDriver
        driver = setup_web_driver()
        scraper = TweetScraper(driver)

        # Combinar todos los términos de búsqueda
        terminos_busqueda = (
            CRISIS_HASHTAGS +
            KEYWORDS +
            SEARCH_PHRASES
        )

        # Contador para estadísticas
        total_tweets = 0
        coordenadas_procesadas = 0
        terminos_procesados = 0

        # Iterar sobre cada coordenada
        for coordenada in COORDENADAS:
            coordenadas_procesadas += 1
            logger.info(f"""
            Procesando coordenada {coordenadas_procesadas}/{len(COORDENADAS)}:
            Latitud: {coordenada[0]}
            Longitud: {coordenada[1]}
            """)

            # Procesar cada término de búsqueda para esta coordenada
            for termino in terminos_busqueda:
                terminos_procesados += 1
                logger.info(f"Procesando término {terminos_procesados}/{len(terminos_busqueda)}: {termino}")

                try:
                    exito = procesar_termino(scraper, termino, coordenada)
                    if exito:
                        total_tweets += 1

                    # Pausa entre términos
                    time.sleep(EXTRACTION_SETTINGS['pausa_entre_terminos'])

                except KeyboardInterrupt:
                    logger.warning("""
                    Proceso interrumpido por el usuario
                    Los tweets extraídos hasta ahora están guardados
                    """)
                    mostrar_estadisticas_finales(
                        fecha_inicio,
                        coordenadas_procesadas,
                        terminos_procesados,
                        total_tweets
                    )
                    sys.exit(0)

                except Exception as e:
                    logger.error(f"Error procesando término: {str(e)}")
                    continue

            # Mostrar progreso después de cada coordenada
            logger.info(f"""
            Progreso actual:
            - Coordenada completada: {coordenada}
            - Coordenadas procesadas: {coordenadas_procesadas}/{len(COORDENADAS)}
            - Términos procesados: {terminos_procesados}
            - Total tweets encontrados: {total_tweets}
            """)

        # Mostrar estadísticas finales
        mostrar_estadisticas_finales(
            fecha_inicio,
            coordenadas_procesadas,
            terminos_procesados,
            total_tweets
        )

    except Exception as e:
        logger.error(f"Error en el proceso principal: {str(e)}")
        sys.exit(1)

    finally:
        try:
            driver.quit()
            logger.info("Navegador cerrado correctamente")
        except:
            pass

if __name__ == "__main__":
    main()