import customtkinter as ctk
from tkinter import messagebox
import datetime
import pandas as pd

from . import api
from . import utils
from . import logic
from .chart_widget import BolsaChart

class BolsaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Bolsa - Finmarkets Pro")
        self.root.geometry("1100x900")

        # Cargar datos y tema
        self.archivo_json = "nombres.json"
        self.nombres_conocidos = utils.cargar_configuracion(self.archivo_json)
        self.theme = utils.cargar_tema("theme.json")

        self.datos_busqueda = logic.preparar_datos_busqueda(self.nombres_conocidos)

        self.selected_id = "77447"
        self.df = None 
        self.chart_widget = None 

        self._init_ui()

    def _init_ui(self):
        self.root.configure(fg_color=self.theme["window_bg"])
        
        # Configuración del Grid Principal
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1) # El gráfico (fila 2) se expande

        # --- PANEL DE CONTROL (Fila 0) ---
        control_frame = ctk.CTkFrame(self.root, fg_color=self.theme["frame_bg"])
        control_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Hacemos que la columna 1 (Buscador) se expanda
        control_frame.grid_columnconfigure(1, weight=1) 
        control_frame.grid_columnconfigure((0, 2, 3, 4), weight=0) # Los demás fijos

        # 0. Label Instrumento
        ctk.CTkLabel(control_frame, text="Instrumento:", font=("Roboto", 14, "bold"), text_color=self.theme["text_main"]).grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")

        # 1. Buscador (Expandible)
        self.entry_busqueda = ctk.CTkEntry(
            control_frame, 
            placeholder_text="Buscar empresa, nemo o ID...",
            fg_color=self.theme["input_bg"],
            text_color=self.theme["text_main"],
            height=35
        )
        self.entry_busqueda.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        nombre_inicial = self.nombres_conocidos.get(self.selected_id, "ITAUCL")
        self.entry_busqueda.insert(0, nombre_inicial)

        self.entry_busqueda.bind("<KeyRelease>", self._on_key_release)
        self.entry_busqueda.bind("<FocusIn>", self._on_focus_in)

        # 2. Label Periodo
        ctk.CTkLabel(control_frame, text="Periodo:", text_color=self.theme["text_main"]).grid(row=0, column=2, padx=10, pady=15)

        # 3. ComboBox Periodo
        self.entry_span = ctk.CTkComboBox(
            control_frame, 
            values=["1D", "5D", "1M", "3M", "6M", "1Y"], 
            width=80,
            height=35,
            fg_color=self.theme["input_bg"],
            text_color=self.theme["text_main"]
        )
        self.entry_span.set("1D") 
        self.entry_span.grid(row=0, column=3, padx=10, pady=15)

        # 4. Botón Consultar
        self.btn_run = ctk.CTkButton(
            control_frame, 
            text="Consultar", 
            command=self.ejecutar_consulta, 
            fg_color=self.theme["primary_button"],
            hover_color=self.theme["primary_button_hover"],
            text_color="white",
            width=120,
            height=35
        )
        self.btn_run.grid(row=0, column=4, padx=(10, 20), pady=15)

        # --- LISTA FLOTANTE ---
        self.lista_sugerencias = ctk.CTkScrollableFrame(
            self.root, 
            height=200, 
            fg_color=self.theme["frame_bg"], 
            corner_radius=5,
            border_width=1,
            border_color=self.theme["text_secondary"]
        )
        self.lista_sugerencias_visible = False

        # --- CALCULADORA (Fila 1) ---
        calc_frame = ctk.CTkFrame(self.root, fg_color=self.theme["frame_bg"])
        calc_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Configuración grid calculadora:
        # Col 0: Label, Col 1: Monto, Col 2: Fecha Label, Col 3: Fecha (Expand), Col 4: Hoy, Col 5: Calc, Col 6: Res
        calc_frame.grid_columnconfigure(3, weight=1) 

        # 0. Label Calc
        ctk.CTkLabel(calc_frame, text="Calculadora:", font=("Roboto", 14, "bold"), text_color=self.theme["text_main"]).grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")

        # 1. Entry Monto
        self.entry_monto = ctk.CTkEntry(calc_frame, width=120, height=35, placeholder_text="Monto $", fg_color=self.theme["input_bg"], text_color=self.theme["text_main"])
        self.entry_monto.grid(row=0, column=1, padx=5, pady=15)

        # 2. Label Fecha
        ctk.CTkLabel(calc_frame, text="Fecha:", text_color=self.theme["text_main"]).grid(row=0, column=2, padx=(15, 5), pady=15)

        # 3. Entry Fecha (Expandible)
        self.entry_fecha = ctk.CTkEntry(calc_frame, height=35, placeholder_text="YYYY-MM-DD HH:MM", fg_color=self.theme["input_bg"], text_color=self.theme["text_main"])
        self.entry_fecha.grid(row=0, column=3, padx=5, pady=15, sticky="ew")
        
        # 4. Botón Hoy
        ctk.CTkButton(
            calc_frame, 
            text="Hoy", 
            width=60, 
            height=35,
            command=self._set_hoy, 
            fg_color=self.theme["secondary_button"],
            hover_color=self.theme["secondary_button_hover"],
            text_color=self.theme["text_main"]
        ).grid(row=0, column=4, padx=5, pady=15)

        # 5. Botón Calcular
        ctk.CTkButton(calc_frame, text="Calcular", width=100, height=35, command=self.calcular_retorno, fg_color=self.theme["success"], text_color="white").grid(row=0, column=5, padx=10, pady=15)
        
        # 6. Resultado
        self.lbl_resultado_calc = ctk.CTkLabel(calc_frame, text="---", font=("Roboto", 16, "bold"), text_color=self.theme["text_main"])
        self.lbl_resultado_calc.grid(row=0, column=6, padx=(10, 20), pady=15)

        # --- GRÁFICO (Fila 2) ---
        plot_container = ctk.CTkFrame(self.root, fg_color="transparent") 
        plot_container.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        plot_container.grid_rowconfigure(1, weight=1)
        plot_container.grid_columnconfigure(0, weight=1)

        # Barra de estadísticas
        stats_frame = ctk.CTkFrame(plot_container, fg_color="transparent", height=40)
        stats_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 5))
        # Usamos pack para la barra de estado, es más flexible para alineación izq/der
        
        self.lbl_precio = ctk.CTkLabel(stats_frame, text="Precio: ---", font=("Roboto", 20, "bold"), text_color=self.theme["text_main"])
        self.lbl_precio.pack(side="left", padx=10)
        
        self.lbl_minmax = ctk.CTkLabel(stats_frame, text="Min/Max: ---", font=("Roboto", 12), text_color=self.theme["text_main"])
        self.lbl_minmax.pack(side="left", padx=15)
        
        self.lbl_estado_mercado = ctk.CTkLabel(stats_frame, text="---", font=("Roboto", 12, "bold"))
        self.lbl_estado_mercado.pack(side="right", padx=10)
        
        self.lbl_actualizacion = ctk.CTkLabel(stats_frame, text="Actualizado: ---", font=("Roboto", 10, "italic"), text_color=self.theme["text_secondary"])
        self.lbl_actualizacion.pack(side="right", padx=15)

        # Marco del Gráfico
        self.chart_frame = ctk.CTkFrame(plot_container, fg_color=self.theme["frame_bg"])
        self.chart_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        self.chart_widget = BolsaChart(self.chart_frame, self.theme)
        self._actualizar_estado_mercado()

        self.root.bind("<Button-1>", self._check_click_outside)

    # --- Métodos de Interfaz ---
    def _on_key_release(self, event):
        texto = self.entry_busqueda.get().lower()
        self._actualizar_sugerencias(texto)

    def _on_focus_in(self, event):
        self._actualizar_sugerencias(self.entry_busqueda.get().lower())

    def _actualizar_sugerencias(self, texto_filtro):
        for widget in self.lista_sugerencias.winfo_children():
            widget.destroy()

        count = 0
        limit = 30 
        for item in self.datos_busqueda:
            if count >= limit: break
            if texto_filtro in item["search"]:
                btn = ctk.CTkButton(
                    self.lista_sugerencias,
                    text=item["label"],
                    anchor="w",
                    fg_color="transparent",
                    text_color=self.theme["text_main"],
                    hover_color=self.theme["list_hover"],
                    height=25,
                    command=lambda i=item: self._seleccionar_item(i)
                )
                btn.pack(fill="x", padx=2, pady=1)
                count += 1
        if count > 0: self._mostrar_lista()
        else: self._ocultar_lista()

    def _mostrar_lista(self):
        # Ajuste preciso de la posición
        x = self.entry_busqueda.winfo_x() + 20 
        # Sumamos la altura del entry + un pequeño padding
        y = self.entry_busqueda.winfo_y() + self.entry_busqueda.winfo_height() + 25 
        w = self.entry_busqueda.winfo_width()
        
        self.lista_sugerencias.configure(width=w, height=200)
        self.lista_sugerencias.place(x=x, y=y)
        self.lista_sugerencias.lift() 
        self.lista_sugerencias_visible = True

    def _ocultar_lista(self):
        self.lista_sugerencias.place_forget()
        self.lista_sugerencias_visible = False

    def _seleccionar_item(self, item):
        self.selected_id = item["id"]
        self.entry_busqueda.delete(0, "end")
        self.entry_busqueda.insert(0, item["nombre"])
        self._ocultar_lista()

    def _check_click_outside(self, event):
        if self.lista_sugerencias_visible:
            try:
                widget_under_mouse = self.root.winfo_containing(event.x_root, event.y_root)
                if widget_under_mouse is not self.entry_busqueda and \
                   not str(widget_under_mouse).startswith(str(self.lista_sugerencias)):
                    self._ocultar_lista()
            except: pass

    def _set_hoy(self):
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

    def ejecutar_consulta(self):
        time_span = self.entry_span.get()
        if not self.selected_id:
            messagebox.showwarning("Atención", "Selecciona un instrumento.")
            return

        try:
            self.df = api.obtener_datos_mercado(self.selected_id, time_span)
            self.update_stats()
            nombre = self.nombres_conocidos.get(self.selected_id, self.selected_id)
            self.chart_widget.draw_chart(self.df, nombre)
        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

        self._actualizar_estado_mercado()

    def update_stats(self):
        if self.df is None: return
        ultimo = self.df.iloc[-1]['valor']
        maximo = self.df['valor'].max()
        minimo = self.df['valor'].min()
        
        self.lbl_precio.configure(text=f"Precio: ${ultimo:,.2f}")
        self.lbl_minmax.configure(text=f"Min: ${minimo:,.2f} | Max: ${maximo:,.2f}")
        self.lbl_actualizacion.configure(text=f"Actualizado: {datetime.datetime.now().strftime('%H:%M:%S')}")

    def _actualizar_estado_mercado(self):
        texto, color_key = logic.obtener_estado_mercado()
        self.lbl_estado_mercado.configure(text=texto, text_color=self.theme[color_key])

    def calcular_retorno(self):
        if self.df is None: 
            messagebox.showwarning("Error", "Carga datos primero.")
            return
        
        try:
            monto = float(self.entry_monto.get())
            fecha_obj = datetime.datetime.strptime(self.entry_fecha.get(), "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos.")
            return

        resultados = logic.calcular_ganancia_historica(self.df, monto, fecha_obj)
        ganancia = resultados["ganancia"]
        pct = resultados["porcentaje"]
        
        color = self.theme["success"] if ganancia >= 0 else self.theme["danger"]
        self.lbl_resultado_calc.configure(text=f"${ganancia:,.0f} ({pct:.2f}%)", text_color=color)
        
        nombre = self.nombres_conocidos.get(self.selected_id, "")
        self.chart_widget.draw_chart(self.df, nombre, compra_point=(resultados["fecha_encontrada"], resultados["precio_compra"]))