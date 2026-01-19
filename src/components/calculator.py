import customtkinter as ctk
import datetime

class CalculatorPanel(ctk.CTkFrame):
    def __init__(self, parent, theme, on_calcular_callback):
        super().__init__(parent, fg_color=theme["frame_bg"])
        self.theme = theme
        self.on_calcular = on_calcular_callback
        
        self._init_widgets()

    def _init_widgets(self):
        self.grid_columnconfigure(3, weight=1)

        # Label Título
        ctk.CTkLabel(self, text="Calculadora:", font=("Roboto", 14, "bold"), 
                     text_color=self.theme["text_main"]).grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")

        # Input Monto
        self.entry_monto = ctk.CTkEntry(self, width=120, height=35, placeholder_text="Monto $", 
                                        fg_color=self.theme["input_bg"], text_color=self.theme["text_main"])
        self.entry_monto.grid(row=0, column=1, padx=5, pady=15)

        # Input Fecha
        ctk.CTkLabel(self, text="Fecha:", text_color=self.theme["text_main"]).grid(row=0, column=2, padx=(15, 5), pady=15)
        
        self.entry_fecha = ctk.CTkEntry(self, height=35, placeholder_text="YYYY-MM-DD HH:MM", 
                                        fg_color=self.theme["input_bg"], text_color=self.theme["text_main"])
        self.entry_fecha.grid(row=0, column=3, padx=5, pady=15, sticky="ew")

        # Botón Hoy
        ctk.CTkButton(
            self, text="Hoy", width=60, height=35, command=self._set_hoy,
            fg_color=self.theme["secondary_button"], hover_color=self.theme["secondary_button_hover"],
            text_color=self.theme["text_main"]
        ).grid(row=0, column=4, padx=5, pady=15)

        # Botón Calcular
        ctk.CTkButton(
            self, text="Calcular", width=100, height=35, command=self._trigger_calcular,
            fg_color=self.theme["success"], text_color="white"
        ).grid(row=0, column=5, padx=10, pady=15)

        # Label Resultado
        self.lbl_resultado = ctk.CTkLabel(self, text="---", font=("Roboto", 16, "bold"), text_color=self.theme["text_main"])
        self.lbl_resultado.grid(row=0, column=6, padx=(10, 20), pady=15)

    def _set_hoy(self):
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

    def _trigger_calcular(self):
        monto = self.entry_monto.get()
        fecha = self.entry_fecha.get()
        self.on_calcular(monto, fecha)

    def mostrar_resultado(self, texto, es_ganancia=True):
        color = self.theme["success"] if es_ganancia else self.theme["danger"]
        self.lbl_resultado.configure(text=texto, text_color=color)