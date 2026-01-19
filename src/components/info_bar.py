import customtkinter as ctk
import datetime

class InfoBar(ctk.CTkFrame):
    def __init__(self, parent, theme):
        super().__init__(parent, fg_color="transparent", height=40)
        self.theme = theme
        self._init_widgets()

    def _init_widgets(self):
        self.lbl_precio = ctk.CTkLabel(self, text="Precio: ---", font=("Roboto", 20, "bold"), text_color=self.theme["text_main"])
        self.lbl_precio.pack(side="left", padx=10)
        
        self.lbl_minmax = ctk.CTkLabel(self, text="Min/Max: ---", font=("Roboto", 12), text_color=self.theme["text_main"])
        self.lbl_minmax.pack(side="left", padx=15)
        
        self.lbl_estado = ctk.CTkLabel(self, text="---", font=("Roboto", 12, "bold"))
        self.lbl_estado.pack(side="right", padx=10)
        
        self.lbl_update = ctk.CTkLabel(self, text="Actualizado: ---", font=("Roboto", 10, "italic"), text_color=self.theme["text_secondary"])
        self.lbl_update.pack(side="right", padx=15)

    def actualizar_datos(self, precio_actual, min_val, max_val):
        self.lbl_precio.configure(text=f"Precio: ${precio_actual:,.2f}")
        self.lbl_minmax.configure(text=f"Min: ${min_val:,.2f} | Max: ${max_val:,.2f}")
        self.lbl_update.configure(text=f"Actualizado: {datetime.datetime.now().strftime('%H:%M:%S')}")

    def actualizar_estado_mercado(self, texto, color_key):
        color = self.theme.get(color_key, self.theme["text_main"])
        # Si el tema devuelve una tupla (light, dark), elegimos según modo (simplificación)
        if isinstance(color, (list, tuple)):
            mode = ctk.get_appearance_mode()
            color = color[0] if mode == "Light" else color[1]
            
        self.lbl_estado.configure(text=texto, text_color=color)