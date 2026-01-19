import customtkinter as ctk
# Importamos los componentes desde la carpeta hermana (components)
from ..components.control_panel import ControlPanel
from ..components.calculator import CalculatorPanel
from ..components.info_bar import InfoBar
from ..components.chart import BolsaChart

class MainView(ctk.CTkFrame):
    def __init__(self, master, theme, nombres_conocidos, datos_busqueda, callbacks):
        super().__init__(master, fg_color=theme["window_bg"])
        self.theme = theme
        self.callbacks = callbacks # Diccionario con funciones (ej: 'consultar', 'calcular')
        
        # Referencias a los componentes
        self.control_panel = None
        self.calc_panel = None
        self.info_bar = None
        self.chart_widget = None

        self._setup_layout(master, nombres_conocidos, datos_busqueda)

    def _setup_layout(self, root_window, nombres_conocidos, datos_busqueda):
        # Configuración del Grid Principal de la Vista
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # El área del gráfico se expande

        # 1. Panel de Control (Buscador)
        self.control_panel = ControlPanel(
            parent=self,
            theme=self.theme,
            nombres_conocidos=nombres_conocidos,
            datos_busqueda=datos_busqueda,
            on_consultar_callback=self.callbacks['on_consultar'],
            root_window=root_window # Necesario para la lista flotante
        )
        self.control_panel.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # 2. Panel Calculadora
        self.calc_panel = CalculatorPanel(
            parent=self,
            theme=self.theme,
            on_calcular_callback=self.callbacks['on_calcular']
        )
        self.calc_panel.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # 3. Área Gráfica (Contenedor)
        plot_container = ctk.CTkFrame(self, fg_color="transparent")
        plot_container.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        plot_container.grid_rowconfigure(1, weight=1)
        plot_container.grid_columnconfigure(0, weight=1)

        # 3.1 Barra de Información
        self.info_bar = InfoBar(plot_container, self.theme)
        self.info_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 5))

        # 3.2 Gráfico
        chart_frame = ctk.CTkFrame(plot_container, fg_color=self.theme["frame_bg"])
        chart_frame.grid(row=1, column=0, sticky="nsew")
        
        self.chart_widget = BolsaChart(chart_frame, self.theme)

    # Métodos para actualizar la vista desde el Controlador
    def actualizar_grafico(self, df, nombre_instrumento, compra_point=None):
        self.chart_widget.draw_chart(df, nombre_instrumento, compra_point)

    def actualizar_info_bar(self, precio, minimo, maximo):
        self.info_bar.actualizar_datos(precio, minimo, maximo)

    def actualizar_estado_mercado(self, texto, color_key):
        self.info_bar.actualizar_estado_mercado(texto, color_key)

    def mostrar_resultado_calculadora(self, texto, es_ganancia):
        self.calc_panel.mostrar_resultado(texto, es_ganancia)

    def obtener_id_seleccionado(self):
        return self.control_panel.selected_id