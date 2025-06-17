
# Detección de Estrés en Redes Sociales durante Crisis Energética en Ecuador (2024)

![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
![Licencia](https://img.shields.io/badge/license-MIT-green)
![Workflow](https://img.shields.io/badge/Workflow-CRISP--DM-blueviolet)

## Tabla de Contenidos

- [Características Principales](#características-principales)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos Técnicos](#requisitos-técnicos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Resultados Destacados](#resultados-destacados)
- [Licencia](#licencia)
- [Contacto](#contacto)
- [Referencias Técnicas](#referencias-técnicas)
- [Créditos](#créditos)

## Características Principales

- Extracción ética de datos mediante Web Scraping (Playwright/Selenium) con protocolos de privacidad.
- Procesamiento avanzado de NLP:
  - Tokenización con NLTK.
  - Lematización con Stanza.
  - Generación de embeddings con FastText.
- Modelado con SVM optimizado mediante Optuna-TPE.
- Evaluación exhaustiva con métricas para problemas desbalanceados.
- Integración con corpus MentalRiskES para entrenamiento complementario.

## Estructura del Proyecto

```
deteccion-estres-redes/
├── TAREA-1-EXTRACCION-DATOS/
│   ├── Playwright_Scraper/       # Extracción rápida (100 tweets/15s)
│   ├── Selenium_Scraper/         # Alternativa estable (1.2 tweets/min)
│   └── Twitter_API_Scraper/      # Extra con API oficial (opcional)
├── TAREA-2-ANALISIS-LIMPIEZA/
│   └── limpieza_final.ipynb      # Pipeline completo de limpieza
├── TAREA-3-EXTRACCION-CARACTERISTICAS/
│   └── procesamiento_textual.ipynb  # NLP y embeddings
├── TAREA-4-ENTRENAMIENTO-Y-AJUSTE-HIPERPARAMETROS/
│   └── entrenamiento_modelos.ipynb  # SVM + Optuna-TPE
└── TAREA-5-METRICAS/
    └── evaluacion_metricas.ipynb    # Análisis comparativo
```

## Requisitos Técnicos

- Python 3.9+
- 16GB RAM (recomendado para procesamiento de embeddings)
- SSD para manejo eficiente de datasets
- CUDA (opcional para aceleración GPU)

## Instalación

Clonar repositorio:

```bash
git clone https://github.com/DiegoFernandoLojanTN/TIC_Analisis_Sentimientos_SVM_OPTUNA.git
```

Crear y activar entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows
```

Instalar dependencias base:

```bash
pip install -r requirements_base.txt
```

## Uso

### 1. Extracción de Datos

```bash
# Opción recomendada (Playwright)
cd TAREA-1-EXTRACCION-DATOS/Playwright_Scraper
pip install -r requirements.txt
python main.py --keywords "palabras clave (o entrar al apartado keywords)" --max_tweets 500
```

### 2. Limpieza y Preprocesamiento

```bash
cd TAREA-2-ANALISIS-LIMPIEZA
jupyter notebook limpieza_final.ipynb
```

Procesos automáticos:

- Hasheo SHA-256 de metadatos sensibles
- Filtrado por idioma (español)
- Normalización de texto
- Exportación a CSV limpio

### 3. Extracción de Características

```bash
cd TAREA-3-EXTRACCION-CARACTERISTICAS
jupyter notebook procesamiento_textual.ipynb
```

Flujo incluido:

- Tokenización y lematización
- Generación de embeddings (128-dim) con FastText
- Balanceo con SMOTE
- Clasificación binaria

> ⚠️ Nota importante: En esta sección se genera el archivo `fasttext_estres.model.wv.vectors_ngrams.npy`, que contiene los vectores de n-gramas subpalabra generados por el modelo FastText entrenado. Debido a su tamaño (~1GB), no se encuentra en este repositorio.

> 📥 Puedes descargarlo desde el siguiente enlace:  
[Drive - fasttext_estres.model.wv.vectors_ngrams.npy](https://drive.google.com/drive/folders/1FMycNIdyez94pudQLozHRWrVbuPHtAv2?usp=sharing)

### 4. Entrenamiento de Modelos

```bash
cd TAREA-4-ENTRENAMIENTO-Y-AJUSTE-HIPERPARAMETROS
jupyter notebook entrenamiento_modelos.ipynb
```

Opciones:

- SVM base (configuración por defecto - Conjunto de datos Twitter y CorpusMentalRiskES)
- SVM optimizado (100 trials con Optuna-TPE en el Conjunto de datos Twitter y 50 trials con CorpusMentalRiskES)
- Validación cruzada (5 folds)

### 5. Evaluación de Resultados

```bash
cd TAREA-5-METRICAS
jupyter notebook evaluacion_metricas.ipynb
```

Métricas generadas:

- Matrices de confusión
- Curvas ROC y Precision-Recall
- Reporte de clasificación completo

## Resultados Destacados

| Dataset       | Modelo         | Exactitud | F1-score | Recall  | Vectores Soporte |
|---------------|----------------|-----------|----------|---------|------------------|
| Twitter/X     | SVM Base       | 91.16%    | 91.14%   | 91.14%  | 50.9%            |
| Twitter/X     | SVM+Optuna     | 92.63%    | 92.60%   | 92.41%  | 45.2%            |
| MentalRiskES  | SVM Base       | 95.86%    | 95.93%   | 97.81%  | 27.0%            |
| MentalRiskES  | SVM+Optuna     | 97.18%    | 97.23%   | 99.17%  | 20.0%            |


## Licencia

Distribuido bajo licencia MIT. Ver archivo `LICENSE` para más información.

## Contacto

- **Autor Principal:** Diego Fernando Lojan Tenesaca
- **Director:** Ing. Luis Antonio Chamba Eras, PhD  
- **Repositorio:** [[https://github.com/tu-usuario/deteccion-estres-redes](https://github.com/tu-usuario/deteccion-estres-redes)](https://github.com/DiegoFernandoLojanTN/TIC_Analisis_Sentimientos_SVM_OPTUNA.git)

## Referencias Técnicas

- [Optuna Documentation](https://optuna.org/)
- [Scikit-learn SVM Guide](https://scikit-learn.org/stable/modules/svm.html)
- [FastText for Text Classification](https://fasttext.cc/)

## Créditos

Este trabajo utiliza el corpus MentalRiskES para el entrenamiento complementario y comparativo:

```bibtex
@inproceedings{marmol-romero-etal-2024-mentalriskes,
    title = "{M}ental{R}isk{ES}: A new corpus for early detection of mental disorders in {S}panish",
    author = "Mármol-Romero, Ana María  and
      Moreno-Muñoz, Antonio  and
      Plaza-del-Arco, Flor Miriam  and
      Molina-González, M. Dolores  and
      Martín-Valdivia, M. Teresa  and
      Ureña-López, L. Alfonso  and
      Montejo-Ráez, Arturo",
    booktitle = "Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024)",
    month = may,
    year = "2024",
    pages = "11204--11214",
    publisher = "ELRA and ICCL",
    url = "https://aclanthology.org/2024.lrec-main.978"
}
```

Repositorio oficial del corpus: [https://github.com/sinai-uja/corpusMentalRiskES](https://github.com/sinai-uja/corpusMentalRiskES)
