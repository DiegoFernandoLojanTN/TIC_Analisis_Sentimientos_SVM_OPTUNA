"""
Gestor de checkpoints para el crawler de Twitter.

Este módulo maneja el guardado y carga de checkpoints para permitir
pausar y reanudar el proceso de scraping, incluyendo información geográfica.
"""

import json
import os
from datetime import datetime
from src.utils.logger import logger

class CheckpointManager:
    """Maneja el guardado y carga de checkpoints del crawler."""

    def __init__(self, termino_busqueda: str, coordenada: tuple):
        """
        Inicializa el gestor de checkpoints.

        Args:
            termino_busqueda: Término de búsqueda actual
            coordenada: Tupla (lat, lon) de la coordenada actual
        """
        self.checkpoint_dir = 'data/checkpoints'
        self.termino_busqueda = termino_busqueda
        self.coordenada = coordenada

        # Crear nombre de archivo de checkpoint incluyendo coordenadas
        lat, lon = coordenada
        termino_limpio = termino_busqueda.replace(' ', '_').replace('"', '').replace('AND', '_')
        self.checkpoint_file = os.path.join(
            self.checkpoint_dir,
            f'checkpoint_{termino_limpio}_lat{lat}_lon{lon}.json'
        )

        # Crear directorio si no existe
        os.makedirs(self.checkpoint_dir, exist_ok=True)

        # Registrar inicio de sesión
        logger.info(f"Checkpoint inicializado para término '{termino_busqueda}' en coordenadas ({lat}, {lon})")

    def guardar_checkpoint(self, ultimo_tweet_id: str, tweets_procesados: int, scroll_count: int):
        """
        Guarda el progreso actual en un archivo de checkpoint.

        Args:
            ultimo_tweet_id: ID del último tweet procesado
            tweets_procesados: Número de tweets procesados
            scroll_count: Número de scrolls realizados
        """
        lat, lon = self.coordenada
        checkpoint_data = {
            'ultimo_tweet_id': ultimo_tweet_id,
            'tweets_procesados': tweets_procesados,
            'scroll_count': scroll_count,
            'timestamp': datetime.now().isoformat(),
            'termino_busqueda': self.termino_busqueda,
            'coordenadas': {
                'latitud': lat,
                'longitud': lon
            },
            'fecha_inicio': datetime.now().strftime('%Y-%m-%d'),
            'estado': 'en_progreso'
        }

        try:
            # Guardar checkpoint con formato legible
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            logger.info(f"""Checkpoint guardado:
                Archivo: {self.checkpoint_file}
                Tweets procesados: {tweets_procesados}
                Último tweet: {ultimo_tweet_id}
                Coordenadas: ({lat}, {lon})
            """)
        except Exception as e:
            logger.error(f"Error al guardar checkpoint: {str(e)}")
            raise

    def cargar_checkpoint(self) -> dict:
        """
        Carga el último checkpoint guardado.

        Returns:
            dict: Datos del checkpoint o None si no existe
        """
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Verificar integridad del checkpoint
                required_keys = ['ultimo_tweet_id', 'tweets_procesados', 'scroll_count', 'coordenadas']
                if all(key in data for key in required_keys):
                    lat, lon = self.coordenada
                    logger.info(f"""Checkpoint cargado:
                        Archivo: {self.checkpoint_file}
                        Tweets procesados: {data['tweets_procesados']}
                        Coordenadas: ({lat}, {lon})
                        Fecha: {data.get('fecha_inicio', 'No disponible')}
                    """)
                    return data
                else:
                    logger.warning(f"Checkpoint corrupto o incompleto: {self.checkpoint_file}")
                    return None
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar checkpoint JSON: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error al cargar checkpoint: {str(e)}")
            return None

        return None

    def marcar_completado(self):
        """Marca el checkpoint actual como completado."""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r+', encoding='utf-8') as f:
                    data = json.load(f)
                    data['estado'] = 'completado'
                    data['fecha_completado'] = datetime.now().isoformat()
                    f.seek(0)
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    f.truncate()
                logger.info(f"Checkpoint marcado como completado: {self.checkpoint_file}")
        except Exception as e:
            logger.error(f"Error al marcar checkpoint como completado: {str(e)}")

    def eliminar_checkpoint(self):
        """Elimina el archivo de checkpoint actual."""
        try:
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
                logger.info(f"Checkpoint eliminado: {self.checkpoint_file}")
        except Exception as e:
            logger.error(f"Error al eliminar checkpoint: {str(e)}")

    def get_estado_actual(self) -> dict:
        """
        Obtiene el estado actual del proceso de scraping.

        Returns:
            dict: Estado actual del proceso
        """
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return {
                    'termino': self.termino_busqueda,
                    'coordenadas': self.coordenada,
                    'tweets_procesados': data.get('tweets_procesados', 0),
                    'estado': data.get('estado', 'desconocido'),
                    'ultima_actualizacion': data.get('timestamp', None)
                }
        except Exception as e:
            logger.error(f"Error al obtener estado actual: {str(e)}")

        return {
            'termino': self.termino_busqueda,
            'coordenadas': self.coordenada,
            'tweets_procesados': 0,
            'estado': 'no_iniciado',
            'ultima_actualizacion': None
        }