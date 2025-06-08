"""
Modelo de datos para representar tweets y sus atributos.

Este módulo define la estructura de datos para almacenar la información
de los tweets extraídos, incluyendo todos sus metadatos, contenido y
datos de geolocalización.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import dateutil.parser

@dataclass(frozen=True)  # Hacemos la clase inmutable para que sea hasheable
class Tweet:
    """
    Clase que representa un tweet con todos sus atributos relevantes.
    """

    id: str
    autor: str
    nombre_completo: str
    contenido: str
    fecha_publicacion: str
    retweets: int
    likes: int
    hashtag: str
    vistas: Optional[int]
    comentarios: int
    guardados: int
    url_imagen: Optional[str]
    url_video: Optional[str]
    url_preview_video: Optional[str]
    hashtags: tuple  # Cambiado de List a tuple para que sea hasheable
    url: str
    coordenada_lat: Optional[float] = None  # Nueva: latitud de la búsqueda
    coordenada_lon: Optional[float] = None  # Nueva: longitud de la búsqueda
    sentimiento: Optional[str] = None       # Nueva: análisis de sentimiento
    categoria_estres: Optional[str] = None  # Nueva: categorización del estrés

    def __post_init__(self):
        """
        Realiza validaciones y conversiones después de la inicialización.
        """
        # Convertimos la lista de hashtags a tupla para que sea hasheable
        object.__setattr__(self, 'hashtags', tuple(self.hashtags) if isinstance(self.hashtags, list) else self.hashtags)

        # Convertir contadores a enteros
        object.__setattr__(self, 'retweets', self._parse_count(self.retweets))
        object.__setattr__(self, 'likes', self._parse_count(self.likes))
        object.__setattr__(self, 'comentarios', self._parse_count(self.comentarios))
        object.__setattr__(self, 'guardados', self._parse_count(self.guardados))

        if isinstance(self.vistas, str):
            object.__setattr__(self, 'vistas', self._parse_count(self.vistas))

        # Validar coordenadas
        if self.coordenada_lat is not None:
            object.__setattr__(self, 'coordenada_lat', float(self.coordenada_lat))
        if self.coordenada_lon is not None:
            object.__setattr__(self, 'coordenada_lon', float(self.coordenada_lon))

    def __eq__(self, other):
        """Define cuándo dos tweets son iguales."""
        if not isinstance(other, Tweet):
            return False
        return self.id == other.id

    def __hash__(self):
        """Define el hash del tweet basado en su ID único."""
        return hash(self.id)

    @staticmethod
    def _parse_count(value: str) -> int:
        """
        Convierte strings de contadores a enteros.
        Ejemplo: '1.5K' -> 1500, '2M' -> 2000000
        """
        if isinstance(value, int):
            return value
        if not value or value.strip() == '':
            return 0

        value = value.strip().upper()
        multipliers = {'K': 1000, 'M': 1000000, 'B': 1000000000}

        try:
            if value[-1] in multipliers:
                number = float(value[:-1])
                return int(number * multipliers[value[-1]])
            return int(float(value))
        except (ValueError, IndexError):
            return 0

    def _parse_date(self, date_str: str) -> str:
        """
        Parsea una fecha de Twitter a formato ISO.
        """
        try:
            # Usar dateutil.parser para parsear la fecha
            dt = dateutil.parser.parse(date_str)
            # Convertir a formato ISO sin microsegundos
            return dt.strftime('%Y-%m-%dT%H:%M:%S%z')
        except:
            return date_str

    def to_dict(self) -> dict:
        """
        Convierte el tweet a un diccionario para exportación a CSV.
        """
        return {
            'tweet_id': self.id,
            'autor': self.autor,
            'nombre_completo': self.nombre_completo,
            'contenido': self.contenido,
            'fecha_publicacion': self._parse_date(self.fecha_publicacion),
            'retweets': self.retweets,
            'likes': self.likes,
            'hashtags': self.hashtag,
            'vistas': self.vistas,
            'comentarios': self.comentarios,
            'guardados': self.guardados,
            'url_imagen': self.url_imagen,
            'url_video': self.url_video,
            'url_preview_video': self.url_preview_video,
            'hashtags_encontrados': ','.join(self.hashtags) if self.hashtags else '',
            'url_tweet': self.url,
            'coordenada_lat': self.coordenada_lat,
            'coordenada_lon': self.coordenada_lon,
            'sentimiento': self.sentimiento,
            'categoria_estres': self.categoria_estres
        }