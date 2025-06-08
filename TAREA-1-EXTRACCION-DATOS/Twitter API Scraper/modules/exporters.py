"""
Módulo para exportar tweets a diferentes formatos.
Contiene clases para exportar a CSV, JSON, etc.
"""
import os
import csv
import json
from datetime import datetime

class BaseExporter:
    """Clase base para exportadores de tweets."""

    def __init__(self, filename):
        """
        Inicializa el exportador base.

        Args:
            filename (str): Ruta al archivo de salida
        """
        self.filename = filename
        self.data = []
        self.last_save_count = 0
        self.auto_save_threshold = 100  # Guardar automáticamente cada 100 tweets

    def export(self, tweet_data):
        """
        Añade un tweet a los datos a exportar.

        Args:
            tweet_data (dict): Datos del tweet
        """
        self.data.append(tweet_data)

        # Auto-guardar periódicamente para evitar pérdida de datos
        if len(self.data) - self.last_save_count >= self.auto_save_threshold:
            self.auto_save()

    def auto_save(self):
        """Guarda automáticamente los datos para evitar pérdida en caso de error."""
        self.save()
        self.last_save_count = len(self.data)
        print(f"Auto-guardado: {self.last_save_count} tweets guardados en {self.filename}")

    def save(self):
        """
        Guarda los datos en un archivo.
        Debe ser implementado por las clases hijas.

        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        raise NotImplementedError("Las clases hijas deben implementar este método")


class CSVExporter(BaseExporter):
    """Exportador de tweets a formato CSV."""

    def save(self):
        """
        Guarda los datos en un archivo CSV.

        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)

            # Definir campos
            fieldnames = [
                'id', 'usuario', 'texto', 'fecha', 'retweets', 'likes',
                'enlace', 'categoría', 'consulta', 'es_personal', 'ubicación'
            ]

            # Escribir archivo
            with open(self.filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data)

            return True
        except Exception as e:
            print(f"Error al guardar archivo CSV: {e}")
            # Intentar con un nombre alternativo
            try:
                backup_file = f"{self.filename}.backup.csv"
                with open(backup_file, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.data)
                print(f"Datos guardados en archivo de respaldo: {backup_file}")
                return True
            except Exception as e2:
                print(f"Error al guardar archivo de respaldo CSV: {e2}")
                return False


class JSONExporter(BaseExporter):
    """Exportador de tweets a formato JSON."""

    def save(self):
        """
        Guarda los datos en un archivo JSON.

        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)

            # Escribir archivo
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Error al guardar archivo JSON: {e}")
            # Intentar con un nombre alternativo
            try:
                backup_file = f"{self.filename}.backup.json"
                with open(backup_file, 'w', encoding='utf-8') as file:
                    json.dump(self.data, file, ensure_ascii=False, indent=2)
                print(f"Datos guardados en archivo de respaldo: {backup_file}")
                return True
            except Exception as e2:
                print(f"Error al guardar archivo de respaldo JSON: {e2}")
                return False


class NonRelevantExporter(BaseExporter):
    """Exportador de tweets no relevantes a formato CSV y JSON."""

    def __init__(self, csv_filename, json_filename):
        """
        Inicializa el exportador de tweets no relevantes.

        Args:
            csv_filename (str): Ruta al archivo CSV de salida
            json_filename (str): Ruta al archivo JSON de salida
        """
        self.csv_filename = csv_filename
        self.json_filename = json_filename
        self.data = []
        self.last_save_count = 0
        self.auto_save_threshold = 200  # Guardar automáticamente cada 200 tweets no relevantes

    def export(self, tweet_data):
        """
        Añade un tweet no relevante a los datos a exportar.

        Args:
            tweet_data (dict): Datos del tweet
        """
        self.data.append(tweet_data)

        # Auto-guardar periódicamente
        if len(self.data) - self.last_save_count >= self.auto_save_threshold:
            self.auto_save()

    def auto_save(self):
        """Guarda automáticamente los datos para evitar pérdida en caso de error."""
        self.save()
        self.last_save_count = len(self.data)
        print(f"Auto-guardado: {self.last_save_count} tweets no relevantes guardados")

    def save(self):
        """
        Guarda los datos en archivos CSV y JSON.

        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Crear directorios si no existen
            os.makedirs(os.path.dirname(self.csv_filename), exist_ok=True)
            os.makedirs(os.path.dirname(self.json_filename), exist_ok=True)

            # Guardar CSV
            fieldnames = [
                'id', 'usuario', 'texto', 'fecha', 'retweets', 'likes',
                'enlace', 'motivo_filtrado', 'consulta'
            ]

            with open(self.csv_filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data)

            # Guardar JSON
            with open(self.json_filename, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"Error al guardar archivos de tweets no relevantes: {e}")
            # Intentar con nombres alternativos
            try:
                backup_csv = f"{self.csv_filename}.backup.csv"
                backup_json = f"{self.json_filename}.backup.json"

                with open(backup_csv, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.data)

                with open(backup_json, 'w', encoding='utf-8') as file:
                    json.dump(self.data, file, ensure_ascii=False, indent=2)

                print(f"Datos no relevantes guardados en archivos de respaldo: {backup_csv} y {backup_json}")
                return True
            except Exception as e2:
                print(f"Error al guardar archivos de respaldo para tweets no relevantes: {e2}")
                return False