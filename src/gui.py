import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import pandas as pd

# Importamos nuestros módulos propios
from . import api
from . import utils
from .chart_widget import BolsaChart

class BolsaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Bolsa - Finmarkets Modular")
        self.root.geometry("1000x800")

        self.archivo_json = "nombres.json"
        self.nombres_conocidos = utils.cargar_configuracion(self.archivo_json)
        
        self.df = None 
        self.chart_widget = None 

        self._init_ui()

    def _init_ui(self):
        # --- PANEL DE CONTROL ---
        control_frame = ttk.LabelFrame(self.root, text="1. Configuración de Consulta", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(control_frame, text="ID Notación:").grid(row=0, column=0, padx=5)
        self.entry_id = ttk.Entry(control_frame, width=15)
        self.entry_id.insert(0, "77447") 
        self.entry_id.grid(row=0, column=1, padx=5)

        ttk.Label(control_frame, text="Periodo:").grid(row=0, column=2, padx=5)
        self.entry_span = ttk.Combobox(control_frame, values=["1D", "5D", "1M", "3M", "6M", "1Y"], width=10)
        self.entry_span.current(0) 
        self.entry_span.grid(row=0, column=3, padx=5)

        self.btn_run = ttk.Button(control_frame, text="Consultar Datos", command=self.ejecutar_consulta)
        self.btn_run.grid(row=0, column=4, padx=15)

        # --- PANEL CALCULADORA ---
        calc_frame = ttk.LabelFrame(self.root, text="2. Calculadora de Inversión", padding=10)
        calc_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(calc_frame, text="Monto ($):").grid(row=0, column=0, padx=5)
        self.entry_monto = ttk.Entry(calc_frame, width=15)
        self.entry_monto.grid(row=0, column=1, padx=5)

        ttk.Label(calc_frame, text="Fecha (YYYY-MM-DD HH:MM):").grid(row=0, column=2, padx=5)
        self.entry_fecha = ttk.Entry(calc_frame, width=25)
        self.entry_fecha.grid(row=0, column=3, padx=5)
        
        ttk.Button(calc_frame, text="Hoy", width=5, 
                   command=lambda: self.entry_fecha.insert(0, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
                   ).grid(row=0, column=4, padx=2)

        ttk.Button(calc_frame, text="Calcular", command=self.calcular_retorno).grid(row=0, column=5, padx=15)
        
        self.lbl_resultado_calc = ttk.Label(calc_frame, text="---", font=("Arial", 11, "bold"))
        self.lbl_resultado_calc.grid(row=0, column=6, padx=10)

        # --- ESTADÍSTICAS ---
        stats_frame = ttk.LabelFrame(self.root, text="Estadísticas", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        self.lbl_precio = ttk.Label(stats_frame, text="Precio: ---", font=("Arial", 14, "bold"))
        self.lbl_precio.pack(side="left", padx=20)
        self.lbl_minmax = ttk.Label(stats_frame, text="Min/Max: ---", font=("Arial", 10))
        self.lbl_minmax.pack(side="left", padx=20)

        self.lbl_actualizacion = ttk.Label(stats_frame, text="Última act: ---", font=("Arial", 9, "italic"))
        self.lbl_actualizacion.pack(side="right", padx=10)

        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chart_widget = BolsaChart(self.plot_frame)

    def ejecutar_consulta(self):
        id_nota = self.entry_id.get()
        time_span = self.entry_span.get()
        
        if not id_nota or not time_span:
            messagebox.showerror("Error", "Faltan datos")
            return

        try:
            self.df = api.obtener_datos_mercado(id_nota, time_span)
            
            self.update_stats()
            
            nombre = self.nombres_conocidos.get(id_nota, f"ID: {id_nota}")
            self.chart_widget.draw_chart(self.df, nombre)

        except Exception as e:
            messagebox.showerror("Error", str(e))

        self.root.after(60000, self.ejecutar_consulta)

    def update_stats(self):
        if self.df is None: return
        ultimo = self.df.iloc[-1]['valor']
        maximo = self.df['valor'].max()
        minimo = self.df['valor'].min()
        
        self.lbl_precio.config(text=f"Precio: ${ultimo:,.2f}")
        self.lbl_minmax.config(text=f"Min: ${minimo:,.2f} | Max: ${maximo:,.2f}")

        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        self.lbl_actualizacion.config(text=f"Última actualización: {hora_actual}")

    def calcular_retorno(self):
        if self.df is None: 
            messagebox.showwarning("Error", "Primero carga datos.")
            return
        
        try:
            monto = float(self.entry_monto.get())
            fecha_obj = datetime.datetime.strptime(self.entry_fecha.get(), "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Error", "Revisa monto o fecha (YYYY-MM-DD HH:MM)")
            return

        diff = abs(self.df['fecha'] - fecha_obj)
        idx = diff.idxmin()
        fila = self.df.loc[idx]
        
        precio_compra = fila['valor']
        precio_actual = self.df.iloc[-1]['valor']
        
        unidades = monto / precio_compra
        ganancia = (unidades * precio_actual) - monto
        pct = ((precio_actual - precio_compra) / precio_compra) * 100

        color = "green" if ganancia >= 0 else "red"
        self.lbl_resultado_calc.config(text=f"${ganancia:,.0f} ({pct:.2f}%)", foreground=color)
        
        nombre = self.nombres_conocidos.get(self.entry_id.get(), "")
        self.chart_widget.draw_chart(self.df, nombre, compra_point=(fila['fecha'], precio_compra))