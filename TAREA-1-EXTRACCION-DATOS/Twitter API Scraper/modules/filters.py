"""
Módulo para filtrar tweets.
Contiene funciones para determinar si un tweet es relevante.
"""
import re

from config.keywords import (
    FILTROS_COMUNICADOS, FILTROS_CUENTAS, UBICACIONES_ECUADOR
)

def filtrar_tweet(tweet):
    """
    Determina si un tweet debe ser incluido en los resultados.
    Versión mejorada para capturar más expresiones de estrés.

    Args:
        tweet: Objeto tweet de la API

    Returns:
        tuple: (incluir, motivo) donde incluir es un booleano y motivo es una cadena
    """
    texto = tweet.text.lower()
    nombre_usuario = tweet.user.name.lower()
    descripcion = getattr(tweet.user, 'description', '').lower()

    # Filtrar tweets que son retweets
    if hasattr(tweet, 'retweeted_status') and tweet.retweeted_status:
        return False, "retweet"

    # Ser menos estricto con las respuestas si contienen palabras clave importantes
    if getattr(tweet, 'in_reply_to_status_id', None) is not None:
        # Verificar si contiene palabras clave de alta relevancia
        palabras_alta_relevancia = [
            "estres", "estrés", "estresado", "estresada",
            "crisis", "apagón", "apagon", "apagones",
            "corte", "cortes", "sin luz", "sin electricidad"
        ]

        if any(palabra in texto for palabra in palabras_alta_relevancia):
            # Permitir respuestas que contengan palabras clave importantes
            pass
        else:
            return False, "respuesta"

    # Filtrar cuentas institucionales o de noticias, pero ser menos estricto
    cuenta_institucional = False
    for filtro in FILTROS_CUENTAS:
        if filtro.lower() in nombre_usuario or filtro.lower() in descripcion:
            cuenta_institucional = True
            break

    # Verificar si es una expresión personal a pesar de ser cuenta institucional
    if cuenta_institucional:
        # Expresiones personales fuertes que pueden superar el filtro de cuenta institucional
        expresiones_personales_fuertes = [
            "yo estoy", "me siento", "estoy harto", "estoy harta",
            "no aguanto", "me tiene", "no puedo", "sin dormir"
        ]

        if any(exp in texto for exp in expresiones_personales_fuertes):
            # Permitir tweets de cuentas institucionales si contienen expresiones personales fuertes
            pass
        else:
            return False, "cuenta_institucional"

    # Filtrar comunicados oficiales o noticias, pero ser menos estricto
    es_comunicado = False
    for filtro in FILTROS_COMUNICADOS:
        if filtro.lower() in texto:
            es_comunicado = True
            break

    # Verificar si es una expresión personal a pesar de ser comunicado
    if es_comunicado:
        # Expresiones personales que pueden superar el filtro de comunicado
        if re.search(r'\b(yo|me|mi|mis|estoy|estamos|tengo|tenemos|siento|sentimos)\b', texto):
            # Permitir comunicados si contienen expresiones personales
            pass
        else:
            return False, "comunicado_oficial"

    # Verificar si es una expresión personal (ampliado)
    expresiones_personales_regex = r'\b(yo|me|mi|mis|estoy|estamos|tengo|tenemos|siento|sentimos|harto|harta|cansado|cansada|frustrado|frustrada|desesperado|desesperada|agobiado|agobiada|estresado|estresada|nervioso|nerviosa|ansioso|ansiosa|angustiado|angustiada|preocupado|preocupada)\b'
    if re.search(expresiones_personales_regex, texto):
        return True, "expresion_personal"

    # Verificar si contiene palabras clave de crisis energética y estrés
    palabras_crisis = [
        "apagón", "apagon", "apagones", "corte", "cortes", "sin luz", 
        "sin electricidad", "crisis energética", "crisis energetica"
    ]
    
    palabras_estres = [
        "estrés", "estres", "estresado", "estresada", "nervios", "ansiedad",
        "angustia", "frustración", "frustracion", "desesperación", "desesperacion"
    ]
    
    if any(palabra in texto for palabra in palabras_crisis) and any(palabra in texto for palabra in palabras_estres):
        return True, "crisis_estres"

    # Incluir por defecto si pasa todos los filtros
    return True, "relevante"

def ubicacion_ecuador(tweet):
    """
    Determina si un tweet está relacionado con Ecuador basado en la ubicación
    del usuario, el texto del tweet o la descripción del usuario.

    Args:
        tweet: Objeto tweet de la API

    Returns:
        bool: True si el tweet está relacionado con Ecuador, False en caso contrario
    """
    # Verificar en el texto del tweet
    texto = tweet.text.lower()

    # Verificar en la ubicación del usuario
    ubicacion = getattr(tweet.user, 'location', '').lower()

    # Verificar en la descripción del usuario
    descripcion = getattr(tweet.user, 'description', '').lower()

    # Verificar en el nombre del usuario
    nombre = tweet.user.name.lower()

    # Combinar todos los textos para buscar
    texto_completo = f"{texto} {ubicacion} {descripcion} {nombre}"

    # Buscar menciones a Ecuador
    for ubicacion in UBICACIONES_ECUADOR:
        if ubicacion.lower() in texto_completo:
            return True

    # Si no se encuentra ninguna referencia a Ecuador
    return False

def es_tweet_duplicado(tweet, tweet_ids_procesados):
    """
    Determina si un tweet es duplicado basado en su ID o contenido similar.

    Args:
        tweet: Objeto tweet de la API
        tweet_ids_procesados: Conjunto de IDs de tweets ya procesados

    Returns:
        bool: True si el tweet es duplicado, False en caso contrario
    """
    # Verificar por ID
    if tweet.id in tweet_ids_procesados:
        return True
    
    return False                                                    