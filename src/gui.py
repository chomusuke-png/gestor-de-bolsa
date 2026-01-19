import customtkinter as ctk
from tkinter import messagebox
import datetime

from . import api
from . import utils
from . import logic
from .ui.control_panel import ControlPanel
from .ui.calculator import CalculatorPanel
from .ui.info_bar import InfoBar
# Asumiendo que moviste chart_widget.py a src/ui/chart.py, si no, ajusta el import
from .ui.chart import BolsaChart 

class BolsaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Bolsa - Finmarkets Pro")
        self.root.geometry("1100x900")

        # Carga de Datos y Configuración
        self.nombres_conocidos = utils.cargar_configuracion("nombres.json")
        self.theme = utils.cargar_tema("theme.json")
        self.datos_busqueda = logic.preparar_datos_busqueda(self.nombres_conocidos)
        
        self.df = None 
        
        self._setup_layout()
        self._actualizar_estado_general()

    def _setup_layout(self):
        self.root.configure(fg_color=self.theme["window_bg"])
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        # 1. Panel de Control (Buscador)
        self.control_panel = ControlPanel(
            parent=self.root,
            theme=self.theme,
            nombres_conocidos=self.nombres_conocidos,
            datos_busqueda=self.datos_busqueda,
            on_consultar_callback=self.ejecutar_consulta,
            root_window=self.root
        )
        self.control_panel.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # 2. Panel Calculadora
        self.calc_panel = CalculatorPanel(
            parent=self.root,
            theme=self.theme,
            on_calcular_callback=self.calcular_retorno
        )
        self.calc_panel.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # 3. Área Gráfica (Contenedor)
        plot_container = ctk.CTkFrame(self.root, fg_color="transparent")
        plot_container.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        plot_container.grid_rowconfigure(1, weight=1)
        plot_container.grid_columnconfigure(0, weight=1)

        # 3.1 Barra de Info
        self.info_bar = InfoBar(plot_container, self.theme)
        self.info_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 5))

        # 3.2 Gráfico
        self.chart_frame = ctk.CTkFrame(plot_container, fg_color=self.theme["frame_bg"])
        self.chart_frame.grid(row=1, column=0, sticky="nsew")
        
        self.chart_widget = BolsaChart(self.chart_frame, self.theme)

    def ejecutar_consulta(self, instrumento_id, periodo):
        if not instrumento_id:
            messagebox.showwarning("Atención", "Selecciona un instrumento.")
            return

        try:
            self.df = api.obtener_datos_mercado(instrumento_id, periodo)
            
            # Actualizar Info Bar
            ultimo = self.df.iloc[-1]['valor']
            maximo = self.df['valor'].max()
            minimo = self.df['valor'].min()
            self.info_bar.actualizar_datos(ultimo, minimo, maximo)
            
            # Dibujar Gráfico
            nombre = self.nombres_conocidos.get(instrumento_id, instrumento_id)
            self.chart_widget.draw_chart(self.df, nombre)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo datos: {str(e)}")

        self._actualizar_estado_general()

    def calcular_retorno(self, monto_str, fecha_str):
        if self.df is None:
            messagebox.showwarning("Error", "Carga datos de un instrumento primero.")
            return

        try:
            monto = float(monto_str)
            fecha_obj = datetime.datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Error", "Formato de monto o fecha inválido.")
            return

        # Lógica de cálculo delegada a logic.py
        res = logic.calcular_ganancia_historica(self.df, monto, fecha_obj)
        
        ganancia = res["ganancia"]
        pct = res["porcentaje"]
        
        # Actualizar UI Calculadora
        texto_res = f"${ganancia:,.0f} ({pct:.2f}%)"
        self.calc_panel.mostrar_resultado(texto_res, es_ganancia=(ganancia >= 0))
        
        # Mostrar punto en gráfico
        nombre = self.nombres_conocidos.get(self.control_panel.selected_id, "")
        self.chart_widget.draw_chart(
            self.df, nombre, 
            compra_point=(res["fecha_encontrada"], res["precio_compra"])
        )

    def _actualizar_estado_general(self):
        texto, color_key = logic.obtener_estado_mercado()
        self.info_bar.actualizar_estado_mercado(texto, color_key)