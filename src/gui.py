import customtkinter as ctk
from tkinter import messagebox
import datetime

from . import api
from . import utils
from . import logic
from .config import APP_TITLE, WINDOW_SIZE
from .views.main_view import MainView

class BolsaApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)

        # 1. Carga de Datos y Configuración
        self.nombres_conocidos = utils.cargar_configuracion("nombres.json")
        self.theme = utils.cargar_tema("theme.json")
        self.datos_busqueda = logic.preparar_datos_busqueda(self.nombres_conocidos)
        
        self.df = None 

        # 2. Definir Callbacks (Puente entre Vista y Lógica)
        callbacks = {
            'on_consultar': self.ejecutar_consulta,
            'on_calcular': self.calcular_retorno
        }

        # 3. Inicializar la Vista Principal
        self.main_view = MainView(
            master=self.root,
            theme=self.theme,
            nombres_conocidos=self.nombres_conocidos,
            datos_busqueda=self.datos_busqueda,
            callbacks=callbacks
        )
        # La vista ocupa toda la ventana raíz
        self.main_view.pack(fill="both", expand=True)
        
        # 4. Configuración inicial
        self._actualizar_estado_general()

    def ejecutar_consulta(self, instrumento_id, periodo):
        if not instrumento_id:
            messagebox.showwarning("Atención", "Selecciona un instrumento.")
            return

        try:
            # Lógica pura (API)
            self.df = api.obtener_datos_mercado(instrumento_id, periodo)
            
            # Preparar datos para la vista
            ultimo = self.df.iloc[-1]['valor']
            maximo = self.df['valor'].max()
            minimo = self.df['valor'].min()
            nombre = self.nombres_conocidos.get(instrumento_id, instrumento_id)
            
            # Actualizar la Vista
            self.main_view.actualizar_info_bar(ultimo, minimo, maximo)
            self.main_view.actualizar_grafico(self.df, nombre)
            
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

        # Lógica pura (Cálculo)
        res = logic.calcular_ganancia_historica(self.df, monto, fecha_obj)
        
        # Preparar datos
        texto_res = f"${res['ganancia']:,.0f} ({res['porcentaje']:.2f}%)"
        es_ganancia = res["ganancia"] >= 0
        nombre = self.nombres_conocidos.get(self.main_view.obtener_id_seleccionado(), "")
        
        # Actualizar la Vista
        self.main_view.mostrar_resultado_calculadora(texto_res, es_ganancia)
        self.main_view.actualizar_grafico(
            self.df, 
            nombre, 
            compra_point=(res["fecha_encontrada"], res["precio_compra"])
        )

    def _actualizar_estado_general(self):
        texto, color_key = logic.obtener_estado_mercado()
        self.main_view.actualizar_estado_mercado(texto, color_key)