"""
Configuración del sistema de logging para el crawler.

Este módulo configura el sistema de logging usando loguru para un mejor
seguimiento y debugging del proceso de scraping.
"""

import sys
from loguru import logger
from config.settings import LOG_LEVEL

# Configuración básica del logger
def setup_logger():
    """Configura el sistema de logging con formato personalizado y salida a archivo."""
    
    # Eliminar el handler por defecto
    logger.remove()
    
    # Formato personalizado para los logs
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Agregar handler para la consola
    logger.add(
        sys.stderr,
        format=log_format,
        level=LOG_LEVEL,
        colorize=True
    )
    
    # Agregar handler para archivo
    logger.add(
        "logs/crawler.log",
        format=log_format,
        level=LOG_LEVEL,
        rotation="500 MB",  # Rotar el archivo cuando alcance 500MB
        retention="10 days",  # Mantener logs por 10 días
        compression="zip"  # Comprimir archivos rotados
    )
    
    return logger

# Crear instancia del logger
logger = setup_logger()