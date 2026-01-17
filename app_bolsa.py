import tkinter as tk
from tkinter import ttk, messagebox
import requests
import re
import pandas as pd
import datetime
import json
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

class BolsaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Bolsa - Finmarkets")
        self.root.geometry("1000x800") # Aumenté un poco el alto

        self.archivo_json = "nombres.json"
        self.nombres_conocidos = self.cargar_nombres()
        self.df = None # Aquí guardaremos los datos descargados

        # --- PANEL DE CONTROL (CONSULTA) ---
        control_frame = ttk.LabelFrame(root, text="1. Configuración de Consulta", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(control_frame, text="ID Notación:").grid(row=0, column=0, padx=5)
        self.entry_id = ttk.Entry(control_frame, width=15)
        self.entry_id.insert(0, "77447") 
        self.entry_id.grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="Periodo:").grid(row=0, column=2, padx=5)
        self.entry_span = ttk.Combobox(control_frame, values=["1D", "5D", "1M", "3M", "6M", "1Y"], width=10)
        self.entry_span.current(0) 
        self.entry_span.grid(row=0, column=3, padx=5)

        self.btn_run = ttk.Button(control_frame, text="Consultar Datos", command=self.fetch_data)
        self.btn_run.grid(row=0, column=4, padx=15)

        # --- PANEL DE CALCULADORA (NUEVO) ---
        calc_frame = ttk.LabelFrame(root, text="2. Calculadora de Inversión", padding=10)
        calc_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(calc_frame, text="Monto Invertido ($):").grid(row=0, column=0, padx=5)
        self.entry_monto = ttk.Entry(calc_frame, width=15)
        self.entry_monto.grid(row=0, column=1, padx=5)

        ttk.Label(calc_frame, text="Fecha Compra (YYYY-MM-DD HH:MM):").grid(row=0, column=2, padx=5)
        self.entry_fecha = ttk.Entry(calc_frame, width=25)
        self.entry_fecha.grid(row=0, column=3, padx=5)
        
        # Botón para insertar la fecha actual automáticamente (opcional, ayuda mucho)
        self.btn_now = ttk.Button(calc_frame, text="Hoy", width=5, command=lambda: self.entry_fecha.insert(0, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
        self.btn_now.grid(row=0, column=4, padx=2)

        self.btn_calc = ttk.Button(calc_frame, text="Calcular Ganancia", command=self.calcular_retorno)
        self.btn_calc.grid(row=0, column=5, padx=15)

        self.lbl_resultado_calc = ttk.Label(calc_frame, text="Resultado: ---", font=("Arial", 11, "bold"))
        self.lbl_resultado_calc.grid(row=0, column=6, padx=10)

        # --- PANEL DE ESTADÍSTICAS ---
        stats_frame = ttk.LabelFrame(root, text="Estadísticas Actuales", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=5)

        self.lbl_precio = ttk.Label(stats_frame, text="Precio: ---", font=("Arial", 14, "bold"))
        self.lbl_precio.pack(side="left", padx=20)
        
        self.lbl_minmax = ttk.Label(stats_frame, text="Min/Max: --- / ---", font=("Arial", 10))
        self.lbl_minmax.pack(side="left", padx=20)

        self.lbl_vol = ttk.Label(stats_frame, text="Volumen Total: ---", font=("Arial", 10))
        self.lbl_vol.pack(side="left", padx=20)

        # --- PANEL GRÁFICO ---
        self.plot_frame = tk.Frame(root)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def cargar_nombres(self):
        if os.path.exists(self.archivo_json):
            try:
                with open(self.archivo_json, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error JSON: {e}")
                return {}
        else:
            return {}

    def fetch_data(self):
        id_nota = self.entry_id.get()
        time_span = self.entry_span.get()
        
        if not id_nota or not time_span:
            messagebox.showerror("Error", "Por favor ingresa ID y Periodo")
            return

        url = f"https://bancoestado.finmarketslive.cl/www/chart/datachart.php?ID_NOTATION={id_nota}&TIME_SPAN={time_span}"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                raise Exception(f"Error servidor: {response.status_code}")
            
            raw_data = response.text
            pattern = r"\{date:new Date\((\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\),close:([\d\.]+)(?:,volume:(\d+))?\}"
            matches = re.findall(pattern, raw_data)

            if not matches:
                messagebox.showwarning("Sin datos", "No se encontraron datos. Verifica el ID.")
                return

            data = []
            for m in matches:
                year, month, day, hour, minute, second, close, volume = m
                dt = datetime.datetime(int(year), int(month) + 1, int(day), int(hour), int(minute), int(second))
                data.append({
                    'fecha': dt,
                    'valor': float(close),
                    'volumen': int(volume) if volume else 0
                })

            # Guardamos el DF en la instancia (self) para usarlo en la calculadora
            self.df = pd.DataFrame(data)

            self.update_stats()
            self.update_chart(id_nota)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_stats(self):
        if self.df is None: return
        ultimo = self.df.iloc[-1]['valor']
        maximo = self.df['valor'].max()
        minimo = self.df['valor'].min()
        volumen_total = self.df['volumen'].sum()

        self.lbl_precio.config(text=f"Precio Actual: ${ultimo:,.2f}")
        self.lbl_minmax.config(text=f"Min: ${minimo:,.2f}  |  Max: ${maximo:,.2f}")
        self.lbl_vol.config(text=f"Volumen Acum: {volumen_total:,}")

    def update_chart(self, title_id):
        if self.df is None: return
        self.ax.clear()

        nombre_mostrar = self.nombres_conocidos.get(title_id, f"ID: {title_id}")

        self.ax.plot(self.df['fecha'], self.df['valor'], color='#17375e', linewidth=1.5)
        
        # Formato de fechas
        if self.df['fecha'].iloc[-1].date() == self.df['fecha'].iloc[0].date():
            myFmt = mdates.DateFormatter('%H:%M')
        else:
            myFmt = mdates.DateFormatter('%d/%m/%Y')
            
        self.ax.xaxis.set_major_formatter(myFmt)
        self.figure.autofmt_xdate(rotation=45) 

        self.ax.set_title(f"Instrumento: {nombre_mostrar}", fontsize=12, fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.tick_params(axis='x', labelsize=8)
        
        self.figure.tight_layout()
        self.canvas.draw()

    # --- NUEVA LÓGICA DE CALCULADORA ---
    def calcular_retorno(self):
        if self.df is None or self.df.empty:
            messagebox.showwarning("Error", "Primero debes consultar los datos del gráfico.")
            return

        # 1. Obtener Monto
        try:
            monto_inv = float(self.entry_monto.get())
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido.")
            return

        # 2. Obtener y parsear Fecha
        fecha_str = self.entry_fecha.get()
        try:
            # Intentamos leer el formato YYYY-MM-DD HH:MM
            target_date = datetime.datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha incorrecto.\nUsa: YYYY-MM-DD HH:MM\nEjemplo: 2026-01-15 10:30")
            return

        # 3. Buscar el precio más cercano en el DataFrame cargado
        # Calculamos la diferencia absoluta entre la fecha buscada y todas las fechas del DF
        fechas_diff = abs(self.df['fecha'] - target_date)
        idx_mas_cercano = fechas_diff.idxmin()
        
        fila_historica = self.df.loc[idx_mas_cercano]
        precio_compra = fila_historica['valor']
        fecha_encontrada = fila_historica['fecha']

        # Verificar si la fecha encontrada es razonablemente cercana (opcional, por ahora solo avisamos)
        diff_segundos = abs((fecha_encontrada - target_date).total_seconds())
        # Si la diferencia es muy grande (ej: busco fecha de 2020 en un grafico de 1 Dia), avisamos
        if diff_segundos > 86400 * 2: # 2 dias de diferencia
             if not messagebox.askyesno("Aviso", f"La fecha más cercana encontrada es {fecha_encontrada}.\n¿Deseas continuar con este precio (${precio_compra})?"):
                 return

        # 4. Calcular Ganancia
        precio_actual = self.df.iloc[-1]['valor']
        
        # Cuantas acciones/unidades compramos
        unidades = monto_inv / precio_compra
        
        # Cuanto valen ahora
        valor_actual = unidades * precio_actual
        
        # Diferencia
        ganancia = valor_actual - monto_inv
        porcentaje = ((precio_actual - precio_compra) / precio_compra) * 100

        # 5. Mostrar Resultado
        signo = "+" if ganancia >= 0 else ""
        color = "green" if ganancia >= 0 else "red"
        
        texto_res = f"{signo}${ganancia:,.0f} ({signo}{porcentaje:.2f}%)"
        self.lbl_resultado_calc.config(text=texto_res, foreground=color)
        
        # Marcar en el gráfico el punto de compra
        self.update_chart(self.entry_id.get()) # Limpia grafico
        self.ax.plot(fecha_encontrada, precio_compra, 'ro', label='Compra') # Punto rojo
        self.ax.legend()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = BolsaApp(root)
    root.mainloop()