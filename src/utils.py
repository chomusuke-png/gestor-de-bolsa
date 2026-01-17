import json
import os

def cargar_configuracion(archivo_json):
    """Carga el diccionario desde el archivo JSON si existe."""
    if os.path.exists(archivo_json):
        try:
            with open(archivo_json, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error leyendo {archivo_json}: {e}")
            return {}
    return {}