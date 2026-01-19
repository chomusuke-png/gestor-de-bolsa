import pandas as pd
import datetime

def calcular_ganancia_historica(df: pd.DataFrame, monto_inversion: float, fecha_objetivo):
    diff = abs(df['fecha'] - fecha_objetivo)
    idx = diff.idxmin()
    fila = df.loc[idx]
    
    precio_compra = fila['valor']
    fecha_encontrada = fila['fecha']
    
    precio_actual = df.iloc[-1]['valor']
    
    unidades = monto_inversion / precio_compra
    ganancia = (unidades * precio_actual) - monto_inversion
    porcentaje = ((precio_actual - precio_compra) / precio_compra) * 100
    
    return {
        "ganancia": ganancia,
        "porcentaje": porcentaje,
        "precio_compra": precio_compra,
        "precio_actual": precio_actual,
        "fecha_encontrada": fecha_encontrada
    }

def obtener_estado_mercado():
    now = datetime.datetime.now().time()
    
    start_pre = datetime.time(9, 00)
    start_open = datetime.time(9, 30)
    start_close = datetime.time(15, 45)
    end_market = datetime.time(16, 00)

    if start_pre <= now < start_open:
        return "🟡 Pre-apertura", "status_pre"
    elif start_open <= now < start_close:
        return "🟢 Mercado Abierto", "status_open"
    elif start_close <= now < end_market:
        return "🔴 Cierre (Subasta)", "status_close"
    else:
        return "🌑 Mercado Cerrado", "status_off"

def preparar_datos_busqueda(nombres_conocidos: dict):
    datos = []
    for nid, nombre in nombres_conocidos.items():
        datos.append({
            "id": nid,
            "nombre": nombre,
            "label": f"{nombre} ({nid})",
            "search": f"{nombre} {nid}".lower()
        })
    return datos