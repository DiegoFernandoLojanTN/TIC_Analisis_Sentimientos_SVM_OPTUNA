"""
Gestor de archivos CSV para el almacenamiento de tweets.

Este módulo maneja la escritura y actualización de archivos CSV
que contienen los tweets extraídos, organizados por término de búsqueda,
fecha y coordenadas geográficas.
"""

import os
import pandas as pd
from typing import List
from datetime import datetime
from src.models.tweet import Tweet
from src.utils.logger import logger
from config.settings import (
    CSV_COLUMNS,
    get_output_filename,
    START_DATE
)

class CSVManager:
    """Gestiona el almacenamiento de tweets en archivos CSV."""

    def __init__(self, termino_busqueda: str, coordenada: tuple):
        """
        Inicializa el gestor de archivos CSV.

        Args:
            termino_busqueda: Término de búsqueda actual
            coordenada: Tupla (lat, lon) de la coordenada actual
        """
        self.termino_busqueda = termino_busqueda
        self.coordenada = coordenada
        self.output_dir = 'data/output/tweets'

        # Crear nombre de archivo basado en término, fecha y coordenadas
        self.filename = get_output_filename(
            coordenada=coordenada,
            termino_busqueda=termino_busqueda,
            fecha=START_DATE
        )

        # Asegurar que el directorio existe
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"""CSV Manager inicializado:
            Término: {termino_busqueda}
            Coordenadas: {coordenada}
            Archivo: {self.filename}
        """)

    def guardar_tweets(self, tweets: List[Tweet], modo: str = 'a') -> bool:
        """
        Guarda una lista de tweets en el archivo CSV.

        Args:
            tweets: Lista de objetos Tweet a guardar
            modo: Modo de escritura ('a' para append, 'w' para write)

        Returns:
            bool: True si la operación fue exitosa
        """
        if not tweets:
            logger.warning("No hay tweets para guardar")
            return False

        try:
            # Convertir tweets a formato DataFrame
            tweets_data = []
            for tweet in tweets:
                tweet_dict = tweet.to_dict()
                # Añadir información de coordenadas
                tweet_dict['coordenada_lat'] = self.coordenada[0]
                tweet_dict['coordenada_lon'] = self.coordenada[1]
                tweet_dict['termino_busqueda'] = self.termino_busqueda
                tweets_data.append(tweet_dict)

            df_nuevos = pd.DataFrame(tweets_data)

            # Asegurar que todas las columnas necesarias estén presentes
            for columna in CSV_COLUMNS:
                if columna not in df_nuevos.columns:
                    df_nuevos[columna] = None

            # Reordenar columnas según CSV_COLUMNS
            df_nuevos = df_nuevos[CSV_COLUMNS]

            # Verificar si el archivo existe
            if os.path.exists(self.filename) and modo == 'a':
                # Cargar CSV existente
                df_existente = pd.read_csv(self.filename)

                # Verificar duplicados
                tweets_existentes = set(df_existente['tweet_id'].astype(str))
                df_nuevos = df_nuevos[~df_nuevos['tweet_id'].astype(str).isin(tweets_existentes)]

                if not df_nuevos.empty:
                    # Append solo si hay tweets nuevos
                    df_nuevos.to_csv(self.filename, mode='a', header=False, index=False)
                    logger.info(f"""Tweets guardados en modo append:
                        Archivo: {self.filename}
                        Nuevos tweets: {len(df_nuevos)}
                        Total acumulado: {len(df_existente) + len(df_nuevos)}
                    """)
                else:
                    logger.info("No hay tweets nuevos para guardar")
            else:
                # Crear nuevo archivo
                df_nuevos.to_csv(self.filename, index=False)
                logger.info(f"""Nuevo archivo CSV creado:
                    Archivo: {self.filename}
                    Tweets guardados: {len(df_nuevos)}
                """)

            return True

        except Exception as e:
            logger.error(f"Error al guardar tweets en CSV: {str(e)}", exc_info=True)
            return False

    def cargar_tweets(self) -> pd.DataFrame:
        """
        Carga los tweets existentes del archivo CSV.

        Returns:
            pd.DataFrame: DataFrame con los tweets cargados o None si hay error
        """
        try:
            if os.path.exists(self.filename):
                df = pd.read_csv(self.filename)
                logger.info(f"""Tweets cargados del archivo:
                    Archivo: {self.filename}
                    Total tweets: {len(df)}
                """)
                return df
            else:
                logger.warning(f"No existe el archivo: {self.filename}")
                return None

        except Exception as e:
            logger.error(f"Error al cargar tweets del CSV: {str(e)}", exc_info=True)
            return None

    def obtener_tweets_unicos(self) -> set:
        """
        Obtiene el conjunto de IDs de tweets ya guardados.

        Returns:
            set: Conjunto de IDs de tweets existentes
        """
        try:
            if os.path.exists(self.filename):
                df = pd.read_csv(self.filename)
                return set(df['tweet_id'].astype(str))
            return set()
        except Exception as e:
            logger.error(f"Error al obtener tweets únicos: {str(e)}")
            return set()

    def verificar_duplicados(self, tweets: List[Tweet]) -> List[Tweet]:
        """
        Filtra tweets duplicados comparando con los existentes.

        Args:
            tweets: Lista de tweets a verificar

        Returns:
            List[Tweet]: Lista de tweets sin duplicados
        """
        tweets_existentes = self.obtener_tweets_unicos()
        return [tweet for tweet in tweets if tweet.id not in tweets_existentes]

    def obtener_estadisticas(self) -> dict:
        """
        Obtiene estadísticas del archivo CSV actual.

        Returns:
            dict: Diccionario con estadísticas del archivo
        """
        try:
            if os.path.exists(self.filename):
                df = pd.read_csv(self.filename)
                return {
                    'total_tweets': len(df),
                    'tweets_por_fecha': df['fecha_publicacion'].value_counts().to_dict(),
                    'tweets_por_autor': df['autor'].value_counts().head(10).to_dict(),
                    'promedio_interacciones': {
                        'retweets': df['retweets'].mean(),
                        'likes': df['likes'].mean(),
                        'comentarios': df['comentarios'].mean()
                    },
                    'coordenadas': {
                        'latitud': self.coordenada[0],
                        'longitud': self.coordenada[1]
                    }
                }
            return {}
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {str(e)}")
            return {}

    def limpiar_archivo(self) -> bool:
        """
        Elimina duplicados y ordena el archivo CSV.

        Returns:
            bool: True si la operación fue exitosa
        """
        try:
            if os.path.exists(self.filename):
                df = pd.read_csv(self.filename)
                # Eliminar duplicados
                df_limpio = df.drop_duplicates(subset='tweet_id')
                # Ordenar por fecha
                df_limpio = df_limpio.sort_values('fecha_publicacion', ascending=False)
                # Guardar archivo limpio
                df_limpio.to_csv(self.filename, index=False)
                logger.info(f"""Archivo CSV limpiado:
                    Tweets originales: {len(df)}
                    Tweets después de limpieza: {len(df_limpio)}
                    Duplicados eliminados: {len(df) - len(df_limpio)}
                """)
                return True
            return False
        except Exception as e:
            logger.error(f"Error al limpiar archivo CSV: {str(e)}")
            return False