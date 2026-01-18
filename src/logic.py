import pandas as pd

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