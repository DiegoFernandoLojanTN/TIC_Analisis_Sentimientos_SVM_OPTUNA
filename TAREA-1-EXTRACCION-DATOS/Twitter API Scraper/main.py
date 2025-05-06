"""
Punto de entrada principal para el Twitter Scraper.
Coordina la extracción, filtrado y exportación de tweets.
"""
import os
import sys
import asyncio
import signal
import argparse
from datetime import datetime
import traceback

from colorama import init, Fore, Style, Back

from config.settings import (
    OUTPUT_DIR, NONRELEVANT_DIR, LOG_FILE, MINIMUM_TWEETS,
    DATE_START, DATE_END
)
from modules.scraper import TwitterScraper
from modules.exporters import CSVExporter, JSONExporter, NonRelevantExporter
from modules.utils import setup_logger, print_banner, log_info, log_success, log_error, ProgressTracker

# Inicializar colorama
init(autoreset=True)

# Variable global para el scraper (para poder detenerlo con señales)
scraper = None
progress_tracker = None

def signal_handler(sig, frame):
    """
    Manejador de señales para detener el scraper de forma segura.

    Args:
        sig: Señal recibida
        frame: Frame actual
    """
    print(f"\n{Fore.YELLOW}[INTERRUPCIÓN] Recibida señal de interrupción. Deteniendo scraper de forma segura...{Style.RESET_ALL}")

    if scraper:
        # Guardar checkpoint antes de salir
        scraper.guardar_checkpoint()
        print(f"{Fore.GREEN}[CHECKPOINT] Estado guardado correctamente.{Style.RESET_ALL}")

    if progress_tracker:
        progress_tracker.close()

    print(f"{Fore.YELLOW}[SALIDA] El programa se cerrará en breve. Por favor espere...{Style.RESET_ALL}")

    # Salir con código de error
    sys.exit(1)

async def main():
    """Función principal del programa."""
    global scraper, progress_tracker

    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Mostrar banner
    print_banner()

    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Twitter Scraper para análisis de estrés en crisis energética')
    parser.add_argument('--min-tweets', type=int, default=MINIMUM_TWEETS,
                        help=f'Número mínimo de tweets a recolectar (default: {MINIMUM_TWEETS})')
    parser.add_argument('--start-date', type=str, default=DATE_START,
                        help=f'Fecha de inicio en formato YYYY-MM-DD (default: {DATE_START})')
    parser.add_argument('--end-date', type=str, default=DATE_END,
                        help=f'Fecha de fin en formato YYYY-MM-DD (default: {DATE_END})')
    parser.add_argument('--output-dir', type=str, default=OUTPUT_DIR,
                        help=f'Directorio de salida para tweets relevantes (default: {OUTPUT_DIR})')
    parser.add_argument('--nonrelevant-dir', type=str, default=NONRELEVANT_DIR,
                        help=f'Directorio de salida para tweets no relevantes (default: {NONRELEVANT_DIR})')

    args = parser.parse_args()

    # Configurar logger
    logger = setup_logger(LOG_FILE)
    log_info(logger, f"Iniciando Twitter Scraper - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_info(logger, f"Período de búsqueda: {args.start_date} a {args.end_date}")
    log_info(logger, f"Objetivo: {args.min_tweets} tweets")

    try:
        # Crear directorios de salida si no existen
        os.makedirs(args.output_dir, exist_ok=True)
        os.makedirs(args.nonrelevant_dir, exist_ok=True)

        # Configurar exportadores
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_exporter = CSVExporter(os.path.join(args.output_dir, f"tweets_{timestamp}.csv"))
        json_exporter = JSONExporter(os.path.join(args.output_dir, f"tweets_{timestamp}.json"))

        # Exportador para tweets no relevantes
        nonrelevant_exporter = NonRelevantExporter(
            os.path.join(args.nonrelevant_dir, f"nonrelevant_{timestamp}.csv"),
            os.path.join(args.nonrelevant_dir, f"nonrelevant_{timestamp}.json")
        )

        # Crear barra de progreso
        progress_tracker = ProgressTracker(args.min_tweets, "Recolectando tweets")

        # Inicializar scraper
        scraper = TwitterScraper(logger, progress_tracker)

        # Inicializar cliente de Twitter
        log_info(logger, "Inicializando cliente de Twitter...")
        if not await scraper.inicializar():
            log_error(logger, "No se pudo inicializar el cliente de Twitter. Saliendo...")
            return 1

        # Extraer tweets
        log_info(logger, f"Comenzando extracción de tweets. Objetivo: {args.min_tweets} tweets")
        estadisticas = await scraper.extraer_tweets(
            args.min_tweets,
            [csv_exporter, json_exporter],
            nonrelevant_exporter
        )

        # Guardar datos finales
        log_info(logger, "Guardando datos finales...")
        csv_exporter.save()
        json_exporter.save()
        nonrelevant_exporter.save()

        # Mostrar estadísticas
        scraper.mostrar_estadisticas(estadisticas)

        # Cerrar barra de progreso
        if progress_tracker:
            progress_tracker.close()

        log_success(logger, f"Extracción completada. Se recolectaron {estadisticas['tweets_count']} tweets.")
        log_info(logger, f"Tweets guardados en:")
        log_info(logger, f"  - CSV: {csv_exporter.filename}")
        log_info(logger, f"  - JSON: {json_exporter.filename}")
        log_info(logger, f"Tweets no relevantes guardados en:")
        log_info(logger, f"  - CSV: {nonrelevant_exporter.csv_filename}")
        log_info(logger, f"  - JSON: {nonrelevant_exporter.json_filename}")

        return 0

    except Exception as e:
        log_error(logger, f"Error inesperado: {e}")
        traceback.print_exc()

        # Intentar guardar checkpoint en caso de error
        if scraper:
            scraper.guardar_checkpoint()
            log_info(logger, "Se ha guardado un checkpoint para continuar más tarde.")

        return 1

    finally:
        # Cerrar barra de progreso si existe
        if progress_tracker:
            progress_tracker.close()

if __name__ == "__main__":
    # Ejecutar bucle de eventos de asyncio
    exit_code = asyncio.run(main())
    sys.exit(exit_code)