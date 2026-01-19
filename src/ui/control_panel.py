import customtkinter as ctk

class ControlPanel(ctk.CTkFrame):
    def __init__(self, parent, theme, nombres_conocidos, datos_busqueda, on_consultar_callback, root_window):
        super().__init__(parent, fg_color=theme["frame_bg"])
        self.theme = theme
        self.nombres_conocidos = nombres_conocidos
        self.datos_busqueda = datos_busqueda
        self.on_consultar = on_consultar_callback
        self.root_window = root_window # Necesario para que la lista flotante quede encima de todo
        
        self.selected_id = "77447"
        self.lista_visible = False
        
        self._init_widgets()
        self._init_sugerencias_ui()

    def _init_widgets(self):
        self.grid_columnconfigure(1, weight=1)
        
        # Label Instrumento
        ctk.CTkLabel(self, text="Instrumento:", font=("Roboto", 14, "bold"), 
                     text_color=self.theme["text_main"]).grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")

        # Entry Buscador
        self.entry_busqueda = ctk.CTkEntry(
            self, placeholder_text="Buscar empresa, nemo o ID...",
            fg_color=self.theme["input_bg"], text_color=self.theme["text_main"], height=35
        )
        self.entry_busqueda.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        # Configuración inicial
        nombre_inicial = self.nombres_conocidos.get(self.selected_id, "ITAUCL")
        self.entry_busqueda.insert(0, nombre_inicial)
        
        self.entry_busqueda.bind("<KeyRelease>", self._on_key_release)
        self.entry_busqueda.bind("<FocusIn>", self._on_focus_in)

        # Label y Combo Periodo
        ctk.CTkLabel(self, text="Periodo:", text_color=self.theme["text_main"]).grid(row=0, column=2, padx=10, pady=15)
        
        self.entry_span = ctk.CTkComboBox(
            self, values=["1D", "5D", "1M", "3M", "6M", "1Y"], 
            width=80, height=35, fg_color=self.theme["input_bg"], text_color=self.theme["text_main"]
        )
        self.entry_span.set("1D")
        self.entry_span.grid(row=0, column=3, padx=10, pady=15)

        # Botón Consultar
        self.btn_run = ctk.CTkButton(
            self, text="Consultar", command=self._trigger_consultar,
            fg_color=self.theme["primary_button"], hover_color=self.theme["primary_button_hover"],
            text_color="white", width=120, height=35
        )
        self.btn_run.grid(row=0, column=4, padx=(10, 20), pady=15)

    def _init_sugerencias_ui(self):
        # La lista se crea como hija de la ventana raíz para flotar sobre otros widgets
        self.lista_sugerencias = ctk.CTkScrollableFrame(
            self.root_window, height=200, fg_color=self.theme["frame_bg"], 
            corner_radius=5, border_width=1, border_color=self.theme["text_secondary"]
        )
        
        # Detectar clics fuera para cerrar la lista
        self.root_window.bind("<Button-1>", self._check_click_outside, add="+")

    def _trigger_consultar(self):
        periodo = self.entry_span.get()
        self.on_consultar(self.selected_id, periodo)

    def _on_key_release(self, event):
        self._filtrar_lista(self.entry_busqueda.get().lower())

    def _on_focus_in(self, event):
        self._filtrar_lista(self.entry_busqueda.get().lower())

    def _filtrar_lista(self, texto):
        for widget in self.lista_sugerencias.winfo_children():
            widget.destroy()

        count = 0
        limit = 30
        for item in self.datos_busqueda:
            if count >= limit: break
            if texto in item["search"]:
                btn = ctk.CTkButton(
                    self.lista_sugerencias, text=item["label"], anchor="w",
                    fg_color="transparent", text_color=self.theme["text_main"],
                    hover_color=self.theme["list_hover"], height=25,
                    command=lambda i=item: self._seleccionar_item(i)
                )
                btn.pack(fill="x", padx=2, pady=1)
                count += 1
        
        if count > 0: self._mostrar_lista()
        else: self._ocultar_lista()

    def _mostrar_lista(self):
        # Calculamos posición absoluta respecto a la ventana
        x = self.entry_busqueda.winfo_rootx() - self.root_window.winfo_rootx()
        y = (self.entry_busqueda.winfo_rooty() - self.root_window.winfo_rooty()) + self.entry_busqueda.winfo_height() + 5
        w = self.entry_busqueda.winfo_width()
        
        self.lista_sugerencias.configure(width=w)
        self.lista_sugerencias.place(x=x, y=y)
        self.lista_sugerencias.lift()
        self.lista_visible = True

    def _ocultar_lista(self):
        self.lista_sugerencias.place_forget()
        self.lista_visible = False

    def _seleccionar_item(self, item):
        self.selected_id = item["id"]
        self.entry_busqueda.delete(0, "end")
        self.entry_busqueda.insert(0, item["nombre"])
        self._ocultar_lista()

    def _check_click_outside(self, event):
        if self.lista_visible:
            try:
                widget = self.root_window.winfo_containing(event.x_root, event.y_root)
                # Si el clic no fue en el entry ni en la lista, cerrar
                if widget is not self.entry_busqueda and not str(widget).startswith(str(self.lista_sugerencias)):
                    self._ocultar_lista()
            except: pass