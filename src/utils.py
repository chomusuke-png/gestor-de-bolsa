import json
import os
import sys

def cargar_configuracion(archivo_json):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    ruta_completa = os.path.join(base_path, archivo_json)

    if os.path.exists(ruta_completa):
        try:
            with open(ruta_completa, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error leyendo {archivo_json}: {e}")
            return {}
    return {}