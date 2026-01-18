import customtkinter as ctk
from tkinter import messagebox
import datetime
import pandas as pd

# Importamos módulos propios
from . import api
from . import utils
from .chart_widget import BolsaChart

class BolsaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Bolsa - Finmarkets Pro")
        self.root.geometry("1100x900")

        self.archivo_json = "nombres.json"
        self.nombres_conocidos = utils.cargar_configuracion(self.archivo_json)
        
        self.df = None 
        self.chart_widget = None 

        self._init_ui()

    def _init_ui(self):
        # Configurar grid principal para que se expanda bien
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1) # El gráfico (fila 2) se expande

        # --- 1. PANEL DE CONTROL ---
        # Usamos Frame normal y simulamos el título con un Label
        control_frame = ctk.CTkFrame(self.root)
        control_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Título del bloque
        ctk.CTkLabel(control_frame, text="Configuración de Consulta", font=("Roboto", 14, "bold")).grid(row=0, column=0, columnspan=5, pady=(10, 5), sticky="w", padx=15)

        # Inputs
        ctk.CTkLabel(control_frame, text="ID Notación:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_id = ctk.CTkEntry(control_frame, width=140, placeholder_text="Ej: 77447")
        self.entry_id.insert(0, "77447") 
        self.entry_id.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(control_frame, text="Periodo:").grid(row=1, column=2, padx=10, pady=10)
        self.entry_span = ctk.CTkComboBox(control_frame, values=["1D", "5D", "1M", "3M", "6M", "1Y"], width=100)
        self.entry_span.set("1D") 
        self.entry_span.grid(row=1, column=3, padx=10, pady=10)

        self.btn_run = ctk.CTkButton(control_frame, text="Consultar Datos", command=self.ejecutar_consulta, fg_color="#1f6aa5")
        self.btn_run.grid(row=1, column=4, padx=20, pady=10)

        # --- 2. CALCULADORA ---
        calc_frame = ctk.CTkFrame(self.root)
        calc_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(calc_frame, text="Calculadora de Inversión", font=("Roboto", 14, "bold")).grid(row=0, column=0, columnspan=7, pady=(10, 5), sticky="w", padx=15)

        ctk.CTkLabel(calc_frame, text="Monto ($):").grid(row=1, column=0, padx=10, pady=10)
        self.entry_monto = ctk.CTkEntry(calc_frame, width=140, placeholder_text="100000")
        self.entry_monto.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(calc_frame, text="Fecha (YYYY-MM-DD HH:MM):").grid(row=1, column=2, padx=10, pady=10)
        self.entry_fecha = ctk.CTkEntry(calc_frame, width=200)
        self.entry_fecha.grid(row=1, column=3, padx=10, pady=10)
        
        ctk.CTkButton(calc_frame, text="Hoy", width=60, 
                   command=lambda: self._set_hoy()
                   ).grid(row=1, column=4, padx=5, pady=10)

        ctk.CTkButton(calc_frame, text="Calcular", width=100, command=self.calcular_retorno, fg_color="green").grid(row=1, column=5, padx=20, pady=10)
        
        self.lbl_resultado_calc = ctk.CTkLabel(calc_frame, text="---", font=("Roboto", 16, "bold"))
        self.lbl_resultado_calc.grid(row=1, column=6, padx=20, pady=10)

        # --- 3. ESTADÍSTICAS Y GRÁFICO ---
        # Contenedor principal para stats y gráfico
        plot_container = ctk.CTkFrame(self.root)
        plot_container.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        plot_container.grid_rowconfigure(1, weight=1) # El gráfico se expande
        plot_container.grid_columnconfigure(0, weight=1)

        # Barra de estadísticas (dentro del container)
        stats_frame = ctk.CTkFrame(plot_container, fg_color="transparent") # Transparente para integrarse
        stats_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.lbl_precio = ctk.CTkLabel(stats_frame, text="Precio: ---", font=("Roboto", 20, "bold"))
        self.lbl_precio.pack(side="left", padx=20)
        self.lbl_minmax = ctk.CTkLabel(stats_frame, text="Min/Max: ---", font=("Roboto", 12))
        self.lbl_minmax.pack(side="left", padx=20)
        self.lbl_actualizacion = ctk.CTkLabel(stats_frame, text="Última act: ---", font=("Roboto", 10, "italic"), text_color="gray")
        self.lbl_actualizacion.pack(side="right", padx=10)

        # Frame interno para el Canvas de Matplotlib
        self.chart_frame = ctk.CTkFrame(plot_container)
        self.chart_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Instanciamos nuestra clase de gráfico
        self.chart_widget = BolsaChart(self.chart_frame)

    def _set_hoy(self):
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

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
        
        self.lbl_precio.configure(text=f"Precio: ${ultimo:,.2f}")
        self.lbl_minmax.configure(text=f"Min: ${minimo:,.2f} | Max: ${maximo:,.2f}")

        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        self.lbl_actualizacion.configure(text=f"Última actualización: {hora_actual}")

    def calcular_retorno(self):
        if self.df is None: 
            messagebox.showwarning("Error", "Primero carga datos.")
            return
        
        try:
            monto_str = self.entry_monto.get()
            if not monto_str: raise ValueError
            monto = float(monto_str)
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

        color = "#2cc985" if ganancia >= 0 else "#ff4d4d" # Colores brillantes para modo oscuro
        self.lbl_resultado_calc.configure(text=f"${ganancia:,.0f} ({pct:.2f}%)", text_color=color)
        
        nombre = self.nombres_conocidos.get(self.entry_id.get(), "")
        self.chart_widget.draw_chart(self.df, nombre, compra_point=(fila['fecha'], precio_compra))