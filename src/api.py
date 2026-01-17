import requests
import re
import pandas as pd
import datetime

BASE_URL = "https://bancoestado.finmarketslive.cl/www/chart/datachart.php"

def obtener_datos_mercado(id_nota, time_span):
    """
    Descarga y procesa los datos del mercado.
    Retorna: pandas.DataFrame o lanza Exception si falla.
    """
    url = f"{BASE_URL}?ID_NOTATION={id_nota}&TIME_SPAN={time_span}"
    
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Error servidor: {response.status_code}")
    
    raw_data = response.text
    
    # Expresión regular para parsear el JS
    pattern = r"\{date:new Date\((\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\),close:([\d\.]+)(?:,volume:(\d+))?\}"
    matches = re.findall(pattern, raw_data)

    if not matches:
        raise Exception("No se encontraron datos para ese ID/Periodo.")

    data = []
    for m in matches:
        year, month, day, hour, minute, second, close, volume = m
        # JS meses son 0-11, Python 1-12
        dt = datetime.datetime(int(year), int(month) + 1, int(day), int(hour), int(minute), int(second))
        
        data.append({
            'fecha': dt,
            'valor': float(close),
            'volumen': int(volume) if volume else 0
        })

    return pd.DataFrame(data)