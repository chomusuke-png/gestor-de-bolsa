import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import pandas as pd
import numpy as np

# Gráficos
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

# Importamos nuestros módulos propios
from . import api
from . import utils

class BolsaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Bolsa - Finmarkets Modular")
        self.root.geometry("1000x800")

        # Cargar configuración
        self.archivo_json = "nombres.json"
        self.nombres_conocidos = utils.cargar_configuracion(self.archivo_json)
        
        self.df = None 
        self.annot = None

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

        # --- GRÁFICO ---
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas.mpl_connect("motion_notify_event", self.hover)

    def ejecutar_consulta(self):
        id_nota = self.entry_id.get()
        time_span = self.entry_span.get()
        
        if not id_nota or not time_span:
            messagebox.showerror("Error", "Faltan datos")
            return

        try:
            self.df = api.obtener_datos_mercado(id_nota, time_span)
            self.update_stats()
            self.update_chart(id_nota)
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

    def update_chart(self, title_id, compra_point=None):
        if self.df is None: return
        self.ax.clear()

        nombre = self.nombres_conocidos.get(title_id, f"ID: {title_id}")
        self.ax.plot(self.df['fecha'], self.df['valor'], color='#17375e', linewidth=1.5)
        
        # Formato Fechas
        if self.df['fecha'].iloc[-1].date() == self.df['fecha'].iloc[0].date():
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        else:
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        
        self.figure.autofmt_xdate(rotation=45)
        self.ax.set_title(f"Instrumento: {nombre}", fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.6)

        # Dibujar punto de compra si existe
        if compra_point:
            fecha, precio = compra_point
            self.ax.plot(fecha, precio, 'ro', label='Compra')
            self.ax.legend()

        # Tooltip
        self.annot = self.ax.annotate(
            "", 
            xy=(0,0), 
            xytext=(15,15), 
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w", ec="gray", alpha=0.9),
            arrowprops=dict(arrowstyle="->")
        )
        self.annot.set_visible(False)

        self.canvas.draw()

    def hover(self, event):
        if self.df is None or self.annot is None: return
        if event.inaxes != self.ax:
            if self.annot.get_visible():
                self.annot.set_visible(False)
                self.canvas.draw_idle()
            return

        lines = self.ax.get_lines()
        if not lines: return
        line = lines[0]
        x_data = line.get_xdata()
        
        try:
            x_data_nums = mdates.date2num(x_data)
            idx = np.abs(x_data_nums - event.xdata).argmin()
        except Exception:
            return
        
        fila = self.df.iloc[idx]
        fecha = fila['fecha']
        valor = fila['valor']
        self.annot.xy = (x_data[idx], valor)
        
        if self.df['fecha'].iloc[-1].date() == self.df['fecha'].iloc[0].date():
            fecha_str = fecha.strftime("%H:%M")
        else:
            fecha_str = fecha.strftime("%d/%m/%Y %H:%M")
            
        text = f"{fecha_str}\n${valor:,.2f}"
        self.annot.set_text(text)
        self.annot.set_visible(True)
        
        self.canvas.draw_idle()

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
        
        self.update_chart(self.entry_id.get(), compra_point=(fila['fecha'], precio_compra))