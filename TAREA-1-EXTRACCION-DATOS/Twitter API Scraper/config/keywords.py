"""
Definición de palabras clave para la búsqueda de tweets.
Contiene categorías y términos relacionados con manifestaciones de estrés.
"""

# Palabras clave por categoría
PALABRAS_CLAVE = {
    # Palabras clave relacionadas con la crisis energética
    "crisis_energetica": [
        "crisis energética", "crisis energetica", "apagones", "cortes de luz",
        "cortes de energía", "cortes de energia", "sin luz", "sin electricidad",
        "racionamiento eléctrico", "racionamiento electrico", "racionamiento de luz",
        "racionamiento energético", "racionamiento energetico", "escasez energética",
        "escasez energetica", "falta de luz", "falta de electricidad", "falta de energía",
        "falta de energia", "suspensión del servicio eléctrico", "suspension del servicio electrico",
        # Nuevos términos
        "problema eléctrico", "problema electrico", "problema de luz",
        "problema energético", "problema energetico", "crisis de luz",
        "crisis eléctrica", "crisis electrica", "emergencia energética",
        "emergencia energetica", "colapso energético", "colapso energetico",
        "déficit energético", "deficit energetico", "escasez eléctrica",
        "escasez electrica", "falla eléctrica", "falla electrica",
        "interrupción eléctrica", "interrupcion electrica", "sin servicio eléctrico",
        "sin servicio electrico", "corte de electricidad", "cortes de electricidad",
        "suspensión de energía", "suspension de energia", "suspensión eléctrica",
        "suspension electrica", "apagón", "apagon", "apagones", "sin energía",
        "sin energia", "racionamiento", "horario de cortes", "horarios de cortes"
    ],

    # Palabras clave de contexto Ecuador
    "contexto_ecuador": [
        "Ecuador", "ecuatoriano", "ecuatoriana", "ecuatorianos", "ecuatorianas",
        "Quito", "Guayaquil", "Cuenca", "Ambato", "Manta", "Portoviejo", "Machala",
        "Loja", "Esmeraldas", "Santo Domingo", "Ibarra", "Riobamba", "Milagro",
        "Babahoyo", "Quevedo", "Latacunga", "Tulcán", "Tulcan", "Azogues"
    ],

    # Expresiones directas de estrés
    "estres_directo": [
        "estresado", "estresada", "estrés", "estres",
        "estresante", "me estresa", "estresadísimo", "estresadísima",
        "estresándome", "me tiene estresado", "me tiene estresada",
        "estrés máximo", "estres maximo", "nivel de estrés", "nivel de estres",
        "estrés por", "estres por", "tanto estrés", "tanto estres",
        "qué estrés", "que estres", "puro estrés", "puro estres",
        # Nuevos términos
        "estresadísimo", "estresadisimo", "super estresado", "super estresada",
        "muy estresado", "muy estresada", "demasiado estrés", "demasiado estres",
        "estrés total", "estres total", "estrés crónico", "estres cronico",
        "estrés extremo", "estres extremo", "estrés severo", "estres severo",
        "estrés agudo", "estres agudo", "estrés intenso", "estres intenso",
        "estrés constante", "estres constante", "estrés permanente", "estres permanente",
        "estrés diario", "estres diario", "estrés continuo", "estres continuo",
        "estrés persistente", "estres persistente", "estrés prolongado", "estres prolongado"
    ],

    # Manifestaciones físicas de estrés
    "manifestaciones_fisicas": [
        "dolor de cabeza", "migraña", "migrana", "jaqueca",
        "insomnio", "no puedo dormir", "sin dormir", "no duermo",
        "tensión muscular", "tension muscular", "contractura",
        "dolor de espalda", "dolor de cuello", "dolor de hombros",
        "cansancio", "agotamiento", "agotado", "agotada",
        "fatiga", "fatigado", "fatigada", "exhausto", "exhausta",
        "taquicardia", "palpitaciones", "sudoración", "sudoracion",
        "temblor", "temblores", "tiemblo", "me tiemblan"
    ],

    # Manifestaciones psicológicas de estrés
    "manifestaciones_psicologicas": [
        "ansiedad", "ansioso", "ansiosa", "me da ansiedad",
        "angustia", "angustiado", "angustiada", "me angustia",
        "irritable", "irritado", "irritada", "irritabilidad",
        "frustración", "frustracion", "frustrado", "frustrada",
        "desesperación", "desesperacion", "desesperado", "desesperada",
        "preocupación", "preocupacion", "preocupado", "preocupada",
        "nervios", "nervioso", "nerviosa", "me pone nervioso", "me pone nerviosa",
        "mal humor", "malhumorado", "malhumorada", "de mal humor",
        "impotencia", "impotente", "me siento impotente"
    ],

    # Expresiones de malestar general
    "expresiones_malestar": [
        "no aguanto", "no soporto", "insoportable",
        "harto", "harta", "hartazgo", "me tiene harto", "me tiene harta",
        "cansado", "cansada", "cansancio", "me tiene cansado", "me tiene cansada",
        "colapsado", "colapsada", "colapso", "al borde del colapso",
        "saturado", "saturada", "saturación", "saturacion",
        "agobiado", "agobiada", "agobio", "me agobia",
        "abrumado", "abrumada", "me abruma", "abrumador",
        "fastidiado", "fastidiada", "fastidio", "me fastidia",
        "molesto", "molesta", "molestia", "me molesta",
        "qué rabia", "que rabia", "me da rabia", "rabioso", "rabiosa"
    ],

    # Impacto en actividades diarias
    "impacto_actividades": [
        "no puedo trabajar", "imposible trabajar", "difícil trabajar", "dificil trabajar",
        "no puedo estudiar", "imposible estudiar", "difícil estudiar", "dificil estudiar",
        "afecta mi trabajo", "afecta mi estudio", "afecta mis estudios",
        "no rindo", "bajo rendimiento", "rindiendo mal",
        "no me concentro", "falta de concentración", "falta de concentracion",
        "distraído", "distraida", "distracción", "distraccion",
        "improductivo", "improductiva", "improductividad",
        "no avanzo", "no puedo avanzar", "estancado", "estancada",
        "perdiendo tiempo", "pérdida de tiempo", "perdida de tiempo",
        "retrasado", "retrasada", "retraso", "con retraso"
    ]
}

# Filtros para identificar comunicados oficiales o noticias
FILTROS_COMUNICADOS = [
    "comunicado oficial", "comunicado", "informa", "informamos",
    "noticia", "noticias", "última hora", "ultima hora", "urgente",
    "boletín", "boletin", "reporte", "reportamos", "anunciamos",
    "anuncio", "declaración", "declaracion", "declara", "declaramos",
    "oficial", "oficialmente", "ministerio", "gobierno", "autoridades",
    "fuentes oficiales", "según fuentes", "segun fuentes", "confirma",
    "confirmamos", "confirmado", "desmienten", "desmiente", "desmentimos"
]

# Filtros para identificar cuentas institucionales
FILTROS_CUENTAS = [
    "oficial", "noticias", "news", "prensa", "press", "medio", "media",
    "diario", "periódico", "periodico", "revista", "magazine", "tv",
    "televisión", "television", "radio", "fm", "am", "informativo",
    "informativa", "noticiero", "ministerio", "gobierno", "oficial",
    "presidencia", "alcaldía", "alcaldia", "municipio", "municipalidad",
    "prefectura", "gobernación", "gobernacion", "secretaría", "secretaria",
    "institución", "institucion", "empresa", "compañía", "compania"
]

# Combinaciones específicas para búsquedas más efectivas
COMBINACIONES_BUSQUEDA = [
    # Formato: (manifestación, contexto)
    ("estresado", "apagones Ecuador"),
    ("estresada", "sin luz Ecuador"),
    ("cansado", "crisis energética Ecuador"),
    ("cansada", "cortes de luz Ecuador"),
    ("harto", "apagones Ecuador"),
    ("harta", "sin electricidad Ecuador"),
    ("no aguanto", "apagones Ecuador"),
    ("me tiene harto", "sin luz Ecuador"),
    ("me tiene harta", "cortes de luz Ecuador"),
    ("no puedo trabajar", "sin electricidad Ecuador"),
    ("no puedo estudiar", "apagones Ecuador"),
    ("sin dormir", "cortes de luz Ecuador"),
    ("insomnio", "apagones Ecuador"),
    ("desesperado", "crisis energética Ecuador"),
    ("desesperada", "sin luz Ecuador"),
    ("frustrado", "apagones Ecuador"),
    ("frustrada", "cortes de luz Ecuador"),
    ("ansioso", "sin electricidad Ecuador"),
    ("ansiosa", "apagones Ecuador"),
    ("irritado", "sin luz Ecuador"),
    ("irritada", "cortes de luz Ecuador"),
    ("agobiado", "crisis energética Ecuador"),
    ("agobiada", "apagones Ecuador"),
    ("colapsado", "sin electricidad Ecuador"),
    ("colapsada", "cortes de luz Ecuador"),
    ("qué estrés", "apagones Ecuador"),
    ("qué rabia", "sin luz Ecuador"),
    ("qué impotencia", "crisis energética Ecuador"),
    ("dolor de cabeza", "apagones Ecuador"),
    ("migraña", "sin luz Ecuador"),
    ("no puedo dormir", "cortes de luz Ecuador"),
    ("angustia", "crisis energética Ecuador"),
    ("preocupado", "apagones Ecuador"),
    ("preocupada", "sin electricidad Ecuador"),
    ("nervioso", "cortes de luz Ecuador"),
    ("nerviosa", "apagones Ecuador"),
    ("mal humor", "sin luz Ecuador"),
    ("impotencia", "crisis energética Ecuador"),
    ("no me concentro", "apagones Ecuador"),
    ("perdiendo tiempo", "sin luz Ecuador"),
    ("bajo rendimiento", "cortes de luz Ecuador"),
    ("afecta mi trabajo", "apagones Ecuador"),
    ("afecta mis estudios", "sin electricidad Ecuador"),
    # Nuevas combinaciones
    ("estresado", "problema eléctrico Ecuador"),
    ("estresada", "problema de luz Ecuador"),
    ("cansado", "apagón Ecuador"),
    ("cansada", "apagones Ecuador"),
    ("harto", "corte de electricidad Ecuador"),
    ("harta", "cortes de electricidad Ecuador"),
    ("no aguanto", "racionamiento Ecuador"),
    ("me tiene harto", "horario de cortes Ecuador"),
    ("me tiene harta", "horarios de cortes Ecuador"),
    ("no puedo trabajar", "suspensión eléctrica Ecuador"),
    ("no puedo estudiar", "suspensión de energía Ecuador"),
    ("sin dormir", "falla eléctrica Ecuador"),
    ("insomnio", "interrupción eléctrica Ecuador"),
    ("desesperado", "sin servicio eléctrico Ecuador"),
    ("desesperada", "emergencia energética Ecuador"),
    ("frustrado", "colapso energético Ecuador"),
    ("frustrada", "déficit energético Ecuador"),
    ("ansioso", "escasez eléctrica Ecuador"),
    ("ansiosa", "crisis eléctrica Ecuador"),
    ("irritado", "problema energético Ecuador"),
    ("irritada", "crisis de luz Ecuador"),
    ("estrés total", "apagones Ecuador"),
    ("estres extremo", "cortes de luz Ecuador"),
    ("estrés crónico", "crisis energética Ecuador"),
    ("estres severo", "racionamiento eléctrico Ecuador"),
    ("estrés agudo", "sin electricidad Ecuador"),
    ("estres intenso", "falta de luz Ecuador"),
    ("estrés constante", "problema eléctrico Ecuador"),
    ("estres diario", "suspensión del servicio eléctrico Ecuador")
]

# Palabras clave para identificar ubicación en Ecuador
UBICACIONES_ECUADOR = [
    "Ecuador", "Quito", "Guayaquil", "Cuenca", "Ambato", "Manta",
    "Portoviejo", "Machala", "Loja", "Esmeraldas", "Santo Domingo",
    "Ibarra", "Riobamba", "Milagro", "Babahoyo", "Quevedo",
    "Latacunga", "Tulcán", "Tulcan", "Azogues", "Salinas",
    "Daule", "Durán", "Duran", "Otavalo", "Chone", "Quinindé",
    "Quininde", "Santa Elena", "La Libertad", "Samborondón",
    "Samborondon", "Jipijapa", "Huaquillas", "Ventanas", "Buena Fe",
    "Pichincha", "Guayas", "Azuay", "Manabí", "Manabi", "El Oro",
    "Tungurahua", "Loja", "Los Ríos", "Los Rios", "Chimborazo",
    "Imbabura", "Cotopaxi", "Esmeraldas", "Cañar", "Canar",
    "Bolívar", "Bolivar", "Sucumbíos", "Sucumbios", "Morona Santiago",
    "Zamora Chinchipe", "Carchi", "Napo", "Orellana", "Pastaza",
    "Santa Elena", "Santo Domingo de los Tsáchilas", "Santo Domingo de los Tsachilas",
    "Galápagos", "Galapagos", "ecuatoriano", "ecuatoriana", "ecuatorianos",
    "ecuatorianas", "EC", "ECU", "593"
]