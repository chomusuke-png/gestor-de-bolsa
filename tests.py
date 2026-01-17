import requests
import re
import pandas as pd
import datetime
import time

# id pucobre 59108
# id itau 77447

# URL de la API oculta
url = "https://bancoestado.finmarketslive.cl/www/chart/datachart.php?ID_NOTATION=77447&TIME_SPAN=1D"

def obtener_datos():
    try:
        # 1. Obtener los datos crudos
        response = requests.get(url)
        raw_data = response.text

        # 2. Usar Regex para entender el formato "Javascript"
        # Busca patrones tipo: {date:new Date(2026, 0, 15...),close:72.80...}
        pattern = r"\{date:new Date\((\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\),close:([\d\.]+)(?:,volume:(\d+))?\}"
        matches = re.findall(pattern, raw_data)

        data = []
        for m in matches:
            year, month, day, hour, minute, second, close, volume = m
            # OJO: Los meses en JS van de 0 a 11. Sumamos 1.
            dt = datetime.datetime(int(year), int(month) + 1, int(day), int(hour), int(minute), int(second))
            
            entry = {
                'fecha': dt,
                'valor': float(close),
                'volumen': int(volume) if volume else 0
            }
            data.append(entry)

        # 3. Guardar en CSV
        df = pd.DataFrame(data)
        df.to_csv("datos_bolsa.csv", index=False)
        print(f"Datos actualizados: {len(df)} registros encontrados.")

    except Exception as e:
        print(f"Error: {e}")

# Ejecutar
if __name__ == "__main__":
    while True:
        obtener_datos()
        print("Esperando 60 segundos...")
        time.sleep(60)