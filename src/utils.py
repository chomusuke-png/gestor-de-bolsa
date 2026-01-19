import json
import os
import sys

def cargar_configuracion(archivo_json):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        ruta_carpeta = os.path.join(base_path, "assets")
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta_carpeta = os.path.join(base_path, "assets")

    ruta_completa = os.path.join(ruta_carpeta, archivo_json)

    if os.path.exists(ruta_completa):
        try:
            with open(ruta_completa, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"Error leyendo {archivo_json}: {e}")
            return {}
    else:
        print(f"Advertencia: No se encontró {ruta_completa}")
        return {}

def cargar_tema(archivo_json="theme.json"):
    raw_theme = cargar_configuracion(archivo_json)
    theme = {}
    for key, val in raw_theme.items():
        if isinstance(val, list) and len(val) == 2:
            theme[key] = tuple(val)
        else:
            theme[key] = val
    return theme